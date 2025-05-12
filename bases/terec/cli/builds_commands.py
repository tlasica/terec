import plotext as plt
import typer
from rich import box
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from terec.util.cli_util import (
    get_terec_rest_api,
    TerecCallContext,
)
from terec.util import cli_params as params

builds_app = typer.Typer()


def get_builds(org: str, project: str, suite: str, branch: str):
    terec = TerecCallContext.create(org, project)
    # collect response from terec server
    url = f"{terec.url}/history/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/builds"
    query_params = {"branch": branch}
    return get_terec_rest_api(url, query_params)


def get_build(terec: TerecCallContext, suite: str, run_id: int):
    url = f"{terec.url}/tests/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/runs/{run_id}"
    return get_terec_rest_api(url, {})


@builds_app.command()
def history(
    suite: str = params.ARG_SUITE,
    branch: str = params.ARG_BRANCH,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
):
    """
    Prints out the history of runs of given suite and on given branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param to limit number of results
    TODO: add param flag to show ignored
    """
    limit = None
    terec = TerecCallContext.create(org, project)
    data = get_builds(terec.org, terec.prj, suite, branch)
    # print results
    title = f"History of builds of {terec.org}/{terec.prj}/{suite} on branch {branch}"
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
        return "#" * int(num) if num else ""

    for build in data:
        if build.get("url", ""):
            build_id = f"[link={build['url']}]{build['run_id']}[/link]"
        else:
            build_id = f"{build['run_id']}"
        table.add_row(
            build_id,
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


@builds_app.command()
def show(
    suite: str = params.ARG_SUITE,
    run_id: int = params.ARG_RUN_ID,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
):
    """
    Print details of given suite run. [TODO: we need GET for /suite/runs/]
    """
    terec = TerecCallContext.create(org, project)
    data = get_build(terec, suite, run_id)
    pprint(data)


def print_unusable_builds_note(field: str, builds) -> None:
    if builds:
        builds_ids = [f"#{b['run_id']} [{b['tstamp'][:19]}]" for b in builds]
        print()
        print(
            f"Note that {len(builds)} builds did not have data for {field}: {builds_ids}"
        )


def color_for_field(field: str) -> str:
    colors = {
        "fail_count": "red",
        "skip_count": "orange",
    }
    return colors.get(field, None)


@builds_app.command()
def histogram(
    suite: str = params.ARG_SUITE,
    branch: str = params.ARG_BRANCH,
    field: str = params.ARG_BUILD_FIELD,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
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
    suite: str = params.ARG_SUITE,
    branch: str = params.ARG_BRANCH,
    field: str = params.ARG_BUILD_FIELD,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
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
    suite: str = params.ARG_SUITE,
    branch: str = params.ARG_BRANCH,
    org: str = params.OPT_ORG,
    project: str = params.OPT_PRJ,
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
    plt.simple_multiple_bar(
        builds,
        [pass_values, skip_values, fail_values],
        labels=fields,
        colors=["green", "orange", "red"],
    )
    plt.theme("dark")
    plt.show()
    print_unusable_builds_note("pass_count", unusable_data)
