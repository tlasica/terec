import plotext as plt
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
def history(
        suite: str,
        branch: str,
        org: str = None,
        project: str = None):
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
        box=box.ROUNDED,
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
        if num is None:
            return "---"
        else:
            return f"{color}{num}{color}" if num > 0 else str(num)

    def chart(num: str) -> str:
        if num is None:
            return ""
        elif int(num) < 50:
            return "#" * int(num)
        else:
            return "#" * 50 + "(...)"

    for build in data:
        table.add_row(
            str(build["run_id"]),
            str(build["tstamp"])[:19],
            decorated_status(str(build["status"])),
            str(build["total_count"] or "---"),
            str(build["pass_count"] or "---"),
            decorated_number(build["skip_count"], "[yellow]"),
            decorated_number(build["fail_count"], "[red]"),
            chart(build["fail_count"]),
        )

    console = Console()
    console.print()
    console.print(table)


def print_unusable_builds_note(field: str, builds) -> None:
    if builds:
        builds_ids = [f"#{b['run_id']} [{b['tstamp'][:19]}]" for b in builds]
        print()
        print(f"Note that {len(builds)} builds did not have data for {field}: {builds_ids}")


def color_for_field(field: str) -> str:
    colors = {
        "fail_count": "red",
        "skip_count": "orange",
    }
    return colors.get(field, None)


PLOT_BUILD_FIELDS = ["fail_count", "skip_count", "pass_count", "total_count", "duration_sec"]


@builds_app.command()
def histogram(
    suite: str = typer.Argument(help="which suite runs to plot"),
    branch: str = typer.Argument(help="branch to select suite runs"),
    field: str = typer.Option("fail_count", help=f"field to use from {PLOT_BUILD_FIELDS}"),
    org: str = typer.Option(None, help="org id, if not used then TEREC_ORG env var will be used"),
    project: str = typer.Option(None, help="project id, if not used then TEREC_PRJ env var will be used"),
):
    """
    Prints out the histogram of number of test failures for runs of given suite and on given branch.
    Requires TEREC_URL to be set.
    """
    data = get_builds(org, project, suite, branch)
    usable_data = [b for b in data if b[field] is not None]
    unusable_data = [b for b in data if b[field] is None]
    # TODO: Make percentiles?
    # print results
    hist_data = [int(build[field]) for build in usable_data]
    plt.hist(data=hist_data, bins=10, color=color_for_field(field))
    plt.title(f"histogram of {field} per build")
    plt.xlabel(field)
    plt.ylabel(f"#builds with {field}")
    plt.plot_size(None, 25)
    plt.theme("dark")
    plt.show()

    print_unusable_builds_note(field, unusable_data)


@builds_app.command()
def bar(
    suite: str = typer.Argument(help="which suite runs to plot"),
    branch: str = typer.Argument(help="branch to select suite runs"),
    field: str = typer.Option("fail_count", help=f"field to use from {PLOT_BUILD_FIELDS}"),
    org: str = typer.Option(None, help="org id, if not used then TEREC_ORG env var will be used"),
    project: str = typer.Option(None, help="project id, if not used then TEREC_PRJ env var will be used"),
):
    """
    Prints out the plot of number of values for runs of given suite and on given branch.
    Requires TEREC_URL to be set.
    """
    data = get_builds(org, project, suite, branch)
    usable_data = [b for b in data if b[field] is not None]
    unusable_data = [b for b in data if b[field] is None]
    # print results
    builds = [f"#{b['run_id']} [{b['tstamp'][:19]}]" for b in usable_data]
    values = [int(b[field]) for b in usable_data]
    plt.simple_bar(builds, values, title=f"{field}", color=color_for_field(field))
    plt.theme("dark")
    plt.show()
    print_unusable_builds_note(field, unusable_data)


@builds_app.command()
def view(
    suite: str = typer.Argument(help="which suite runs to plot"),
    branch: str = typer.Argument(help="branch to select suite runs"),
    org: str = typer.Option(None, help="org id, if not used then TEREC_ORG env var will be used"),
    project: str = typer.Option(None, help="project id, if not used then TEREC_PRJ env var will be used"),
):
    """
    Prints out the plot of passed/skipped/failed per build.
    Requires TEREC_URL to be set.
    """
    data = get_builds(org, project, suite, branch)
    fields = ["pass_count", "skip_count", "fail_count"]
    usable_data = [b for b in data if b["pass_count"] is not None]
    unusable_data = [b for b in data if b["pass_count"] is None]
    # print results
    builds = [f"#{b['run_id']} [{b['tstamp'][:19]}]" for b in usable_data]
    pass_values = [int(b["pass_count"]) for b in usable_data]
    skip_values = [int(b["skip_count"]) for b in usable_data]
    fail_values = [int(b["fail_count"]) for b in usable_data]
    plt.simple_multiple_bar(builds, [pass_values, skip_values, fail_values],
                            labels=fields, colors=["green", "orange", "red"])
    plt.theme("dark")
    plt.show()
    print_unusable_builds_note("pass_count", unusable_data)
