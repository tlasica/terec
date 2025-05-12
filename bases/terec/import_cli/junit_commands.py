from datetime import datetime
from pathlib import Path
from typing import Optional

import orjson
import requests
import typer

from fastapi.encoders import jsonable_encoder


from terec.api.routers.results import TestSuiteRunInfo
from terec.converters.junit.converter import JunitXmlConverter
from terec.util import cli_params as params
from terec.util.cli_util import env_terec_url

junit_app = typer.Typer(help="JUnit XML import and conversion tools.")


@junit_app.command("convert")
def convert(
    xml_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to JUnit XML file"
    ),
    branch: str = params.ARG_BRANCH,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
    run_id: int = params.ARG_RUN_ID,
):
    """Convert JUnit XML to JSON using the internal converter."""
    xml_content = xml_file.read_text(encoding="utf-8")
    converter = JunitXmlConverter(xml_content)
    suite_runs = [s for s in converter.get_suite_runs()]

    def updated_with_params(s: TestSuiteRunInfo) -> TestSuiteRunInfo:
        s.org = org or s.org or "imported"
        s.project = project or s.project or "imported"
        s.branch = branch
        s.run_id = run_id
        return s

    result = []
    for suite in suite_runs:
        result.append(
            {
                "suite": updated_with_params(suite).model_dump(),
                "tests": [
                    tc.model_dump()
                    for tc in converter.get_test_cases_for_suite(suite.suite)
                ],
            }
        )

    print(
        orjson.dumps(jsonable_encoder(result), option=orjson.OPT_INDENT_2).decode(
            "utf-8"
        )
    )


@junit_app.command("import")
def import_junit(
    xml_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to JUnit XML file"
    ),
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
    branch: str = params.ARG_BRANCH,
    run_id: int = params.ARG_RUN_ID,
    suite: Optional[str] = typer.Option(
        None, help="Test suite name (overrides xml content)"
    ),
):
    # Get API base URL
    try:
        base_url = env_terec_url()
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Parse the XML file
    xml_content = xml_file.read_text(encoding="utf-8")
    converter = JunitXmlConverter(xml_content)

    suite_runs = converter.get_suite_runs()
    if not suite_runs:
        typer.echo("Error: No test suites found in the XML file.", err=True)
        raise typer.Exit(code=1)

    for suite_run in suite_runs:
        suite_run.org = org or suite_run.org or "imported"
        suite_run.project = project or suite_run.project or "imported"
        suite_run.suite = suite or suite_run.suite
        suite_run.branch = branch
        suite_run.run_id = run_id
        if not suite_run.tstamp:
            suite_run.tstamp = datetime.now()

        suite_run_str = f"{suite_run.org}/{suite_run.project}/{suite_run.suite}/{suite_run.branch}/{suite_run.run_id}"

        typer.echo(f"Importing suite run {suite_run_str}...")
        try:
            # Create the suite run via API
            runs_url = f"{base_url}/tests/orgs/{suite_run.org}/runs"
            data = jsonable_encoder(suite_run)
            response = requests.post(runs_url, json=data, timeout=180)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            typer.echo(f"Error creating suite run: {e}", err=True)
            raise typer.Exit(code=1)

        typer.echo(f"Suite run {suite_run_str }created successfully.")

        # Gather and upload test case run info
        test_cases = converter.get_test_cases_for_suite(suite_run.suite)
        if not test_cases:
            typer.echo(
                f"Warning: No test cases found for suite {suite_run_str}.", err=True
            )
            continue

        try:
            # Use the correct endpoint
            test_cases_url = (
                f"{base_url}/tests/orgs/{suite_run.org}/projects/{suite_run.project}"
                f"/suites/{suite_run.suite}/branches/{suite_run.branch}"
                f"/runs/{suite_run.run_id}/tests"
            )
            typer.echo(
                f"Uploading {len(test_cases)} test case(s) for suite '{suite_run_str}'..."
            )
            response = requests.post(
                test_cases_url,
                json=jsonable_encoder(test_cases),
                timeout=180,
            )
            print(response.text)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            typer.echo(f"Error uploading test cases: {e}", err=True)
            raise typer.Exit(code=1)

        typer.echo("Test cases uploaded successfully.")
