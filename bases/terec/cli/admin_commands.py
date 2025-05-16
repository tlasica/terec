from datetime import datetime
from pathlib import Path
from typing import Optional

import orjson
import typer

from terec.api.auth import api_key_headers
from terec.util import cli_params as params
from terec.util.cli_util import env_terec_url

admin_app = typer.Typer(help="Commands to create orgs, projects and suites.")


@admin_app.command(
    "setup",
    short_help="Create org, project and suite.",
    help="Create org, project and suite. Return tokens if private org is requested",
)
def setup_org_project_suite(
    org: str,
    project: str,
    suite: str,
    private: bool = typer.Option(False, "--private", "-p", help="Create private org"),
):
    # create org
    typer.echo(f"Org {org}/{project} created.")
    # create project
    typer.echo(f"Project {org}/{project} created.")
    # create suite
    typer.echo(f"Suite {org}/{project}/{suite} created.")
    # print tokens

    """Convert JUnit XML to JSON using the internal converter."""
    from fastapi.encoders import jsonable_encoder
    from terec.api.routers.results import TestSuiteRunInfo
    from terec.converters.junit.converter import JunitXmlConverter

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
