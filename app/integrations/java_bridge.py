
import json
import subprocess
from pathlib import Path


def run_java_billing_example(
    unit_price: str,
    quantity: int,
) -> dict:
    project_root = Path(__file__).resolve().parents[2]
    java_dir = project_root / "app" / "integrations"

    java_exe = Path(
        r"C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot\bin\java.exe"
    )

    if not java_exe.exists():
        raise FileNotFoundError(
            f"Java executable not found: {java_exe}"
        )

    request = json.dumps({
        "arguments": {
            "unit_price": unit_price,
            "quantity": quantity,
        }
    })

    result = subprocess.run(
        [
            str(java_exe),
            "-cp",
            str(java_dir),
            "BillingBridge",
        ],
        input=request,
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=10,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Java bridge failed: {result.stderr or result.stdout}"
        )

    output_lines = result.stdout.strip().splitlines()

    if not output_lines:
        raise RuntimeError("Java bridge returned no output.")

    return json.loads(output_lines[-1])
