import typer
import json
from pathlib import Path
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
