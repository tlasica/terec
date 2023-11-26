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

tests_app = typer.Typer()


def get_failed_tests(org: str, project: str, suite: str, branch: str):
    terec_url = env_terec_url()
    terec_org = not_none(
        value_or_env(org, "TEREC_ORG"), "org not provided or not set via TEREC_ORG"
    )
    terec_prj = not_none(
        value_or_env(project, "TEREC_PRJ"),
        "project not provided or not set via TEREC_PRJ",
    )
    # collect response from terec server
    url = f"{terec_url}/history/orgs/{terec_org}/projects/{terec_prj}/suites/{suite}/failed-tests"
    query_params = {"branch": branch}
    return get_terec_rest_api(url, query_params)


def test_case_key(test: dict):
    return (
        test["test_run"]["test_package"],
        test["test_run"]["test_suite"],
        test["test_run"]["test_case"],
        test["test_run"]["test_config"],
    )


class FailedTests:
    def __init__(self, data):
        self.data = data

    def unique_test_cases(self):
        res = []
        keys = {}
        for item in self.data:
            k = test_case_key(item)
            if k not in keys:
                keys[k] = 0
                res.append(k)
            keys[k] = keys[k] + 1
        return sorted(keys, key=keys.get, reverse=True)

    def runs_for_test_case(self, key):
        return [x for x in self.data if test_case_key(x) == key]


@tests_app.command()
def failed(suite: str, branch: str, org: str = None, project: str = None):
    """
    Prints out the list of test failures for given suite and branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param to limit number of results
    TODO: add param flag to show ignored
    TODO: use url links for builds if present
    """
    limit = None
    terec_org = value_or_env(org, "TEREC_ORG")
    terec_prj = value_or_env(project, "TEREC_PRJ")
    data = get_failed_tests(org, project, suite, branch)
    # print results
    title = f"Failed tests of {terec_org}/{terec_prj}/{suite} on branch {branch}"
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
    # TODO: shorted names
    table.add_column("package", justify="left")
    table.add_column("class(suite)", justify="left")
    table.add_column("test", justify="left")
    table.add_column("config", style="dim", justify="left")
    table.add_column("group", style="dim", justify="center")
    table.add_column("[red]Fail #[red]", justify="center", style="red")
    table.add_column("[red]Failed in[red]", justify="left", style="red")

    grouped_data = FailedTests(data)
    for test_case in grouped_data.unique_test_cases():
        package, suite, case, config = test_case
        failed_runs = grouped_data.runs_for_test_case(test_case)
        assert failed_runs
        failed_runs_ids = [f"#{run['suite_run']['run_id']}" for run in failed_runs]
        t_group = [x["test_run"]["test_group"] for x in failed_runs][0] or "---"
        table.add_row(
            str(package),
            str(suite),
            str(case),
            str(config),
            str(t_group),
            f"{len(failed_runs)}",
            " ".join(failed_runs_ids[:8]) + ("(...)" if len(failed_runs) > 8 else "")
        )

    console = Console()
    console.print()
    console.print(table)
