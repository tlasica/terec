import typer

from rich.console import Console
from rich.table import Table
from terec.status_cli.util import env_terec_url, value_or_env, get_terec_rest_api, not_none

builds_app = typer.Typer()



@builds_app.command()
def history(suite: str, branch: str, org: str = None, project: str = None):
    """
    Prints out the history of runs of given suite and on given branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param to limit number of results
    TODO: add param flag to show ignored
    """
    terec_url = env_terec_url()
    terec_org = not_none(value_or_env(org, "TEREC_ORG"), "org not provided or not set via TEREC_ORG")
    terec_prj = not_none(value_or_env(project, "TEREC_PRJ"), "project not provided or not set via TEREC_PRJ")
    # collect response from terec server
    url = f"{terec_url}/history/orgs/{terec_org}/projects/{terec_prj}/suites/{suite}/builds"
    query_params = {
        "branch": branch
    }
    data = get_terec_rest_api(url, query_params)
    # print results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Build#", style="dim", width=8, justify="right")
    table.add_column("Date", style="dim", width=19, justify="center")
    table.add_column("Result", justify="center")
    table.add_column("Total", justify="right")
    table.add_column("Pass", justify="right", style="green")
    table.add_column("Fail", justify="right")
    table.add_column("Skip", justify="right")

    def decorated_status(status: str):
        if status == "SUCCESS":
            return f"[green]{status}[green]"
        elif status == "FAILURE":
            return f"[yellow]{status}[yellow]"
        elif status == "ERROR":
            return f"[red]{status}[red]"
        else:
            return status

    def decorated_number(num: int, color: str):
        return f"{color}{num}{color}" if num > 0 else str(num)

    for build in data:
        table.add_row(
            str(build["run_id"]),
            str(build["tstamp"])[:19],
            decorated_status(str(build["status"])),
            str(build["total_count"]),
            str(build["pass_count"]),
            decorated_number(build["fail_count"], "[red]"),
            decorated_number(build["skip_count"], "[yellow]")
        )

    console = Console()
    console.print(table)
