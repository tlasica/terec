import json
import typer

from rich import print

from terec.lib.terec_admin_client import TerecAdminClient
from terec.lib.terec_api_client import TerecApiClient

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
    terec_api_client = TerecApiClient()
    admin_api = TerecAdminClient(terec_api_client)
    # create org
    typer.echo(f"Org {org} created.")
    resp = admin_api.create_org(org, private)
    tokens = {}
    if private:
        tokens = resp.get("tokens", {})
        terec_api_client.set_api_key(tokens.get("admin"))
    # create project
    admin_api.create_project(org, project)
    typer.echo(f"Project {org}/{project} created.")
    # create suite
    admin_api.create_suite(org, project, suite)
    typer.echo(f"Suite {org}/{project}/{suite} created.")
    # print tokens
    if tokens:
        print("Tokens created for private org. [red]Make sure to save them![/red]")
        print(json.dumps(tokens))
