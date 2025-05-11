import typer
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from terec.converters.junit.converter import JunitXmlConverter

junit_app = typer.Typer(help="JUnit XML import and conversion tools.")


@junit_app.command("convert")
def convert(
    xml_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to JUnit XML file"
    ),
    org: str = typer.Option(None, help="Organization name to override in the output"),
    project: str = typer.Option(None, help="Project name to override in the output"),
    branch: str = typer.Option(None, help="Branch name to override in the output"),
    run_id: int = typer.Option(None, help="Run ID to override in the output"),
):
    """Convert JUnit XML to JSON using the internal converter."""
    xml_content = xml_file.read_text(encoding="utf-8")
    converter = JunitXmlConverter(xml_content)
    suite_runs = [s.__dict__ for s in converter.get_suite_runs()]
    # For each suite, also add its cases
    all_cases = {}
    for suite in converter.get_suite_runs():
        all_cases[suite.suite] = [
            c.__dict__ for c in converter.get_test_cases_for_suite(suite.suite)
        ]
    # Convert objects to dicts and handle datetime serialization
    def convert_to_serializable(obj):
        if hasattr(obj, "__dict__"):
            return {
                k: convert_to_serializable(v)
                for k, v in obj.__dict__.items()
                if not k.startswith("_")
            }
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        elif hasattr(obj, "isoformat"):  # Handle datetime
            return obj.isoformat()
        return obj

    # Apply overrides to suite runs
    suite_runs_serialized = []
    for s in suite_runs:
        s_dict = convert_to_serializable(s)
        # Apply overrides if provided
        if org is not None:
            s_dict["org"] = org
        if project is not None:
            s_dict["project"] = project
        if branch is not None:
            s_dict["branch"] = branch
        if run_id is not None:
            s_dict["run_id"] = run_id
        suite_runs_serialized.append(s_dict)

    result = {
        "suite_runs": suite_runs_serialized,
        "test_cases": {
            suite: [convert_to_serializable(c) for c in cases]
            for suite, cases in all_cases.items()
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def get_terec_url() -> str:
    """Get the TEREC API URL from environment variables."""
    # Debug: Print all environment variables
    typer.echo("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("TEREC"):
            typer.echo(f"  {key} = {value}")

    url = os.environ.get("TEREC_URL", None)
    typer.echo(f"Raw TEREC_URL from environment: {url}")

    if not url:
        raise ValueError("TEREC_URL environment variable is not set or empty.")

    # Ensure URL has correct format and remove any trailing slashes
    url = url.rstrip("/")
    typer.echo(f"Using TEREC API URL: {url}")
    return url


@junit_app.command("import")
def import_junit(
    xml_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to JUnit XML file"
    ),
    org: str = typer.Option(None, help="Organization name"),
    project: str = typer.Option(None, help="Project name"),
    branch: str = typer.Option("main", help="Branch name"),
    run_id: Optional[int] = typer.Option(
        None, help="Run ID (auto-generated if not provided)"
    ),
    suite: Optional[str] = typer.Option(
        None, help="Test suite name (defaults to 'junit' if not provided)"
    ),
    url: Optional[str] = typer.Option(
        None, help="API URL (overrides TEREC_URL environment variable)"
    ),
):
    """Import JUnit XML test results into the TEREC system.

    Requires TEREC_URL environment variable to be set.
    """
    # Get API base URL
    try:
        # Use explicitly provided URL if available, otherwise get from environment
        if url:
            base_url = url.rstrip("/")
            typer.echo(f"Using provided API URL: {base_url}")
        else:
            base_url = get_terec_url()
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Parse the XML file
    xml_content = xml_file.read_text(encoding="utf-8")
    converter = JunitXmlConverter(xml_content)

    # Get suite runs and test cases
    suite_runs = converter.get_suite_runs()
    if not suite_runs:
        typer.echo("Error: No test suites found in the XML file.", err=True)
        raise typer.Exit(code=1)

    # Use the first suite run as a template
    suite_run = suite_runs[0]

    # Override values with command line arguments
    suite_run.org = org or suite_run.org or "imported"
    suite_run.project = project or suite_run.project or "imported"
    suite_run.suite = suite or suite_run.suite or "junit"
    suite_run.branch = branch
    if run_id is not None:
        suite_run.run_id = run_id

    # Ensure timestamp is set
    if not suite_run.tstamp:
        suite_run.tstamp = datetime.now()

    # Create suite run via API
    typer.echo(
        f"Creating suite run for {suite_run.org}/{suite_run.project}/{suite_run.suite}..."
    )

    suite_run_data = {
        "org": suite_run.org,
        "project": suite_run.project,
        "suite": suite_run.suite,
        "branch": suite_run.branch,
        "run_id": suite_run.run_id,
        "tstamp": suite_run.tstamp.isoformat(),
        "pass_count": suite_run.pass_count,
        "fail_count": suite_run.fail_count,
        "skip_count": suite_run.skip_count,
        "total_count": suite_run.total_count,
        "duration_sec": suite_run.duration_sec,
        "status": suite_run.status.value
        if hasattr(suite_run.status, "value")
        else suite_run.status,
    }

    # Add optional fields if they exist
    if suite_run.url:
        suite_run_data["url"] = suite_run.url
    if suite_run.commit:
        suite_run_data["commit"] = suite_run.commit

    # Create the suite run
    try:
        # First ensure the organization exists
        org_url = f"{base_url}/admin/orgs"
        org_data = {"name": suite_run.org}
        typer.echo(f"Ensuring organization '{suite_run.org}' exists...")
        response = requests.post(org_url, json=org_data)
        typer.echo(f"Organization creation status: {response.status_code}")

        # Then ensure the project exists
        project_url = f"{base_url}/admin/orgs/{suite_run.org}/projects"
        project_data = {"org": suite_run.org, "name": suite_run.project}
        typer.echo(f"Ensuring project '{suite_run.project}' exists...")
        response = requests.post(project_url, json=project_data)
        typer.echo(f"Project creation status: {response.status_code}")

        # Create/ensure the suite exists
        suite_data = {
            "org": suite_run.org,
            "project": suite_run.project,
            "suite": suite_run.suite,
        }
        suite_url = f"{base_url}/tests/orgs/{suite_run.org}/suites"
        typer.echo(f"Creating suite '{suite_run.suite}' if it doesn't exist...")
        response = requests.post(suite_url, json=suite_data)
        typer.echo(f"Suite creation status: {response.status_code}")

        # Now create the suite run
        runs_url = f"{base_url}/tests/orgs/{suite_run.org}/runs"
        typer.echo(f"Creating suite run...")
        typer.echo(f"Request payload: {json.dumps(suite_run_data, default=str)}")
        response = requests.post(runs_url, json=suite_run_data)
        typer.echo(f"Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"Error creating suite run: {e}", err=True)
        raise typer.Exit(code=1)

    # Get test cases for the suite
    test_cases = converter.get_test_cases_for_suite(suite_run.suite)
    if not test_cases:
        typer.echo("Warning: No test cases found for the suite.", err=True)
        typer.echo("Suite run created successfully, but no test cases were imported.")
        raise typer.Exit(code=0)

    # Prepare test case data for API
    test_case_data = []
    for case in test_cases:
        case_data = {
            "test_package": case.test_package,
            "test_suite": case.test_suite,
            "test_case": case.test_case,
            "test_config": case.test_config,
            "result": case.result.value
            if hasattr(case.result, "value")
            else case.result,
        }

        # Add optional fields if they exist
        if case.test_group:
            case_data["test_group"] = case.test_group
        if case.tstamp:
            case_data["tstamp"] = case.tstamp.isoformat()
        if case.duration_ms is not None:
            case_data["duration_ms"] = case.duration_ms
        if case.stdout:
            case_data["stdout"] = case.stdout
        if case.stderr:
            case_data["stderr"] = case.stderr
        if case.error_stacktrace:
            case_data["error_stacktrace"] = case.error_stacktrace
        if case.error_details:
            case_data["error_details"] = case.error_details
        if case.skip_details:
            case_data["skip_details"] = case.skip_details

        test_case_data.append(case_data)

    # Add test cases via API
    typer.echo(f"Adding {len(test_case_data)} test cases...")
    tests_url = f"{base_url}/tests/orgs/{suite_run.org}/projects/{suite_run.project}/suites/{suite_run.suite}/branches/{suite_run.branch}/runs/{suite_run.run_id}/tests"
    typer.echo(f"Sending test results to: {tests_url}")
    try:
        response = requests.post(tests_url, json=test_case_data)
        typer.echo(f"Response status code: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        typer.echo(
            f"Successfully imported {result.get('test_count', len(test_case_data))} test cases."
        )
    except requests.exceptions.RequestException as e:
        typer.echo(f"Error adding test cases: {e}", err=True)
        raise typer.Exit(code=1)
