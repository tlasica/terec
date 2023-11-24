import plotext as plt
import plotille
import typer
from rich import box

from rich.console import Console
from rich.table import Table
from terec.status_cli.util import (
    env_terec_url,
    value_or_env,
    get_terec_rest_api,
    not_none,
)

builds_app = typer.Typer()


def get_builds(org: str, project: str, suite: str, branch: str):
    terec_url = env_terec_url()
    terec_org = not_none(
        value_or_env(org, "TEREC_ORG"), "org not provided or not set via TEREC_ORG"
    )
    terec_prj = not_none(
        value_or_env(project, "TEREC_PRJ"),
        "project not provided or not set via TEREC_PRJ",
    )
    # collect response from terec server
    url = f"{terec_url}/history/orgs/{terec_org}/projects/{terec_prj}/suites/{suite}/builds"
    query_params = {"branch": branch}
    return get_terec_rest_api(url, query_params)


@builds_app.command()
def history(suite: str, branch: str, org: str = None, project: str = None):
    """
    Prints out the history of runs of given suite and on given branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param to limit number of results
    TODO: add param flag to show ignored
    TODO: use url links for builds if present
    """
    limit = None
    terec_org = value_or_env(org, "TEREC_ORG")
    terec_prj = value_or_env(project, "TEREC_PRJ")
    data = get_builds(org, project, suite, branch)
    # print results
    title = f"History of builds of {terec_org}/{terec_prj}/{suite} on branch {branch}"
    caption = f"limit: {limit}"
    table = Table(
        show_header=True,
        header_style="bold magenta",
        title=title,
        title_justify="left",
        caption=caption,
        caption_justify="left",
        safe_box=True,
        box=box.ROUNDED
    )
    table.add_column("Build#", width=8, justify="right")
    table.add_column("Date", style="dim", width=19, justify="center")
    table.add_column("Result", justify="center")
    table.add_column("Total", justify="right")
    table.add_column("[green]Pass[green]", justify="right", style="green")
    table.add_column("[yellow]Skip[yellow]", justify="right")
    table.add_column("[red]Fail[red]", justify="right")
    table.add_column("[red]# Failed[red]", justify="left", style="red")

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

    def chart(num: int) -> str:
        if num < 50:
            return "#" * num
        else:
            return "#" * 50 + "(...)"

    for build in data:
        table.add_row(
            str(build["run_id"]),
            str(build["tstamp"])[:19],
            decorated_status(str(build["status"])),
            str(build["total_count"]),
            str(build["pass_count"]),
            decorated_number(build["skip_count"], "[yellow]"),
            decorated_number(build["fail_count"], "[red]"),
            chart(int(build["fail_count"])),
        )

    console = Console()
    console.print()
    console.print(table)


@builds_app.command()
def histogram(
    suite: str, branch: str, field: str = None, org: str = None, project: str = None
):
    """
    Prints out the histogram of number of test failures for runs of given suite and on given branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.
    """
    data = get_builds(org, project, suite, branch)
    # print results
    field = field or "fail_count"
    print(
        plotille.histogram(
            X=[int(build[field]) for build in data],
            width=80,
            height=40,
            X_label=field,
            Y_label="# occurrences",
            lc="cyan",
            bg=None,
            color_mode="names",
        )
    )


@builds_app.command()
def bar(
    suite: str, branch: str, field: str = None, org: str = None, project: str = None
):
    """
    Prints out the plot of number of values for runs of given suite and on given branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.
    """
    data = get_builds(org, project, suite, branch)
    # print results
    field = field or "fail_count"
    builds = [f"#{b['run_id']} [{b['tstamp'][:19]}]" for b in data]
    values = [int(b[field]) for b in data]

    colors = {
        "fail_count": "red+",
        "skip_count": "orange+",
    }

    plt.simple_bar(builds, values, title=f"{field}", color=colors.get(field, None))
    plt.show()
