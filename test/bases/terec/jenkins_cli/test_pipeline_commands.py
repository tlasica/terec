from terec.jenkins_cli import main
from typer.testing import CliRunner


runner = CliRunner()


def test_build_export_fails_without_jenkins_url():
    result = runner.invoke(main.app, ["pipeline", "export-build", "job-name", "3"])
    assert result.exit_code != 0
    assert "JENKINS_URL is not set" in str(result.exception)


def test_tests_export_fails_without_jenkins_url():
    result = runner.invoke(main.app, ["pipeline", "export-tests", "job-name", "3"])
    assert result.exit_code != 0
    assert "JENKINS_URL is not set" in str(result.exception)
