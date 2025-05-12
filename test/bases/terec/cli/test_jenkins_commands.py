import os

from terec.cli import main
from typer.testing import CliRunner


runner = CliRunner()


def test_build_export_fails_without_jenkins_url(monkeypatch):
    monkeypatch.delenv("JENKINS_URL", raising=False)
    assert "JENKINS_URL" not in os.environ
    result = runner.invoke(main.app, ["jenkins", "export-build", "job-name", "3"])
    assert result.exit_code != 0
    assert "JENKINS_URL is not set" in str(result.exception)


def test_tests_export_fails_without_jenkins_url(monkeypatch):
    monkeypatch.delenv("JENKINS_URL", raising=False)
    assert "JENKINS_URL" not in os.environ
    result = runner.invoke(main.app, ["jenkins", "export-tests", "job-name", "3"])
    assert result.exit_code != 0
    assert "JENKINS_URL is not set" in str(result.exception)
