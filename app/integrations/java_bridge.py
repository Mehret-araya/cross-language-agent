import json
import os
import shutil
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


class JavaBridgeError(RuntimeError):
    pass


class JavaToolchainUnavailable(JavaBridgeError):
    pass


class JavaBridgeTimeout(JavaBridgeError):
    pass


def _find_executable(name: str) -> str | None:
    executable = shutil.which(name)
    if executable:
        return executable

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        executable_name = f"{name}.exe" if os.name == "nt" else name
        candidate = Path(java_home) / "bin" / executable_name
        if candidate.is_file():
            return str(candidate)
    return None


def _compile_bridge(source: Path, output_dir: Path, project_root: Path) -> None:
    compiler = _find_executable("javac")
    if compiler is None:
        raise JavaToolchainUnavailable(
            "Java bridge source requires javac, but no Java compiler was found."
        )

    try:
        result = subprocess.run(
            [
                compiler,
                "-encoding",
                "UTF-8",
                "-d",
                str(output_dir),
                str(source),
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise JavaBridgeTimeout("Java bridge compilation timed out.") from exc
    except OSError as exc:
        raise JavaToolchainUnavailable(
            f"Unable to run the Java compiler: {exc}"
        ) from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise JavaBridgeError(f"Java bridge compilation failed: {detail}")


def run_java_billing_example(
    unit_price: str,
    quantity: int,
) -> dict:
    project_root = Path(__file__).resolve().parents[2]
    java_dir = project_root / "app" / "integrations"
    java_source = java_dir / "BillingBridge.java"
    java_class = java_dir / "BillingBridge.class"

    java_exe = _find_executable("java")
    if java_exe is None:
        raise JavaToolchainUnavailable(
            "Java runtime was not found. Install a JDK and add java to PATH "
            "or set JAVA_HOME."
        )

    if (
        not java_class.is_file()
        or java_source.stat().st_mtime_ns > java_class.stat().st_mtime_ns
    ):
        _compile_bridge(java_source, java_dir, project_root)

    request = json.dumps({
        "arguments": {
            "unit_price": unit_price,
            "quantity": quantity,
        }
    })

    try:
        result = subprocess.run(
            [
                java_exe,
                "-cp",
                str(java_dir),
                "BillingBridge",
                sys.executable,
            ],
            input=request,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise JavaBridgeTimeout("Java billing example timed out.") from exc
    except OSError as exc:
        raise JavaBridgeError(f"Unable to start the Java bridge: {exc}") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise JavaBridgeError(
            f"Java bridge failed: {detail or f'exit code {result.returncode}'}"
        )

    output_lines = result.stdout.strip().splitlines()

    if not output_lines:
        raise JavaBridgeError("Java bridge returned no output.")

    try:
        response = json.loads(output_lines[-1])
    except json.JSONDecodeError as exc:
        raise JavaBridgeError(
            f"Java bridge returned invalid JSON: {exc.msg}"
        ) from exc

    if not isinstance(response, dict) or "ok" not in response:
        raise JavaBridgeError("Java bridge returned an invalid response.")
    if response["ok"] is not True:
        error = response.get("error")
        if not isinstance(error, str) or not error:
            raise JavaBridgeError("Java bridge reported an unspecified failure.")
        raise JavaBridgeError(f"Java billing example failed: {error}")

    billing_result = response.get("result")
    if not isinstance(billing_result, dict):
        raise JavaBridgeError("Java bridge returned an invalid billing result.")

    unit_price = billing_result.get("unit_price")
    quantity = billing_result.get("quantity")
    total = billing_result.get("total")
    if (
        not isinstance(unit_price, str)
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or not isinstance(total, str)
    ):
        raise JavaBridgeError("Java bridge returned an incomplete billing result.")

    try:
        price_value = Decimal(unit_price)
        total_value = Decimal(total)
    except InvalidOperation as exc:
        raise JavaBridgeError(
            "Java bridge returned invalid billing result values."
        ) from exc
    if (
        not price_value.is_finite()
        or price_value < 0
        or not total_value.is_finite()
        or total_value < 0
        or quantity < 0
    ):
        raise JavaBridgeError("Java bridge returned invalid billing result values.")

    return response
