import os
import subprocess
from pathlib import Path

import pytest

from app.integrations import java_bridge


def test_find_executable_prefers_path(monkeypatch, tmp_path):
    java_on_path = str(tmp_path / "path-java")
    monkeypatch.setattr(java_bridge.shutil, "which", lambda name: java_on_path)
    monkeypatch.setenv("JAVA_HOME", str(tmp_path / "other-java"))

    assert java_bridge._find_executable("java") == java_on_path


def test_find_executable_falls_back_to_java_home(monkeypatch, tmp_path):
    executable_name = "java.exe" if os.name == "nt" else "java"
    java_executable = tmp_path / "bin" / executable_name
    java_executable.parent.mkdir()
    java_executable.touch()
    monkeypatch.setattr(java_bridge.shutil, "which", lambda name: None)
    monkeypatch.setenv("JAVA_HOME", str(tmp_path))

    assert java_bridge._find_executable("java") == str(java_executable)


def test_find_executable_returns_none_when_unavailable(monkeypatch):
    monkeypatch.setattr(java_bridge.shutil, "which", lambda name: None)
    monkeypatch.delenv("JAVA_HOME", raising=False)

    assert java_bridge._find_executable("java") is None


def test_compile_bridge_builds_class_in_requested_directory(tmp_path):
    compiler = java_bridge._find_executable("javac")
    if compiler is None:
        pytest.skip("A Java compiler is required for this integration check.")

    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "integrations"
        / "BillingBridge.java"
    )
    output_dir = tmp_path / "classes"
    output_dir.mkdir()

    java_bridge._compile_bridge(
        source,
        output_dir,
        source.parents[2],
    )

    assert (output_dir / "BillingBridge.class").is_file()


def test_compile_bridge_reports_compiler_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(java_bridge, "_find_executable", lambda name: "javac")
    monkeypatch.setattr(
        java_bridge.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr="compiler error",
        ),
    )

    with pytest.raises(java_bridge.JavaBridgeError, match="compiler error"):
        java_bridge._compile_bridge(
            tmp_path / "BillingBridge.java",
            tmp_path,
            tmp_path,
        )


def test_compile_bridge_reports_timeout(monkeypatch, tmp_path):
    monkeypatch.setattr(java_bridge, "_find_executable", lambda name: "javac")

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="javac", timeout=30)

    monkeypatch.setattr(java_bridge.subprocess, "run", timeout)

    with pytest.raises(java_bridge.JavaBridgeTimeout, match="compilation timed out"):
        java_bridge._compile_bridge(
            tmp_path / "BillingBridge.java",
            tmp_path,
            tmp_path,
        )


@pytest.mark.parametrize(
    ("stdout", "message"),
    [
        ("", "returned no output"),
        ("not-json", "returned invalid JSON"),
        ("[]", "returned an invalid response"),
        ('{"ok": false}', "unspecified failure"),
        ('{"ok": false, "error": "worker failed"}', "worker failed"),
    ],
)
def test_run_java_billing_example_rejects_invalid_worker_responses(
    monkeypatch,
    stdout,
    message,
):
    monkeypatch.setattr(java_bridge, "_find_executable", lambda name: "java")
    monkeypatch.setattr(java_bridge, "_compile_bridge", lambda *args: None)
    monkeypatch.setattr(
        java_bridge.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=stdout,
            stderr="",
        ),
    )

    with pytest.raises(java_bridge.JavaBridgeError, match=message):
        java_bridge.run_java_billing_example("20.00", 3)


def test_run_java_billing_example_reports_missing_runtime(monkeypatch):
    monkeypatch.setattr(java_bridge, "_find_executable", lambda name: None)

    with pytest.raises(
        java_bridge.JavaToolchainUnavailable,
        match="Java runtime",
    ):
        java_bridge.run_java_billing_example("20.00", 3)


def test_run_java_billing_example_reports_launch_timeout(monkeypatch):
    monkeypatch.setattr(java_bridge, "_find_executable", lambda name: "java")
    monkeypatch.setattr(java_bridge, "_compile_bridge", lambda *args: None)

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="java", timeout=10)

    monkeypatch.setattr(java_bridge.subprocess, "run", timeout)

    with pytest.raises(
        java_bridge.JavaBridgeTimeout,
        match="billing example timed out",
    ):
        java_bridge.run_java_billing_example("20.00", 3)
