import asyncio

import typer

from codetiming import Timer
from rich.console import Console
from rich.table import Table
from terec.status_cli.util import (
    env_terec_url,
    value_or_env,
    get_terec_rest_api,
    not_none, typer_table_config, ratio_str, collect_terec_rest_api_calls,
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


def get_test_history_api_call(org: str, project: str, suite: str, branch: str, tpackage: str, tclass: str, tcase: str, tconfig: str):
    terec_url = env_terec_url()
    terec_org = not_none(
        value_or_env(org, "TEREC_ORG"), "org not provided or not set via TEREC_ORG"
    )
    terec_prj = not_none(
        value_or_env(project, "TEREC_PRJ"),
        "project not provided or not set via TEREC_PRJ",
    )
    # collect response from terec server
    url = f"{terec_url}/history/orgs/{terec_org}/projects/{terec_prj}/suites/{suite}/test-runs"
    query_params = {
        "branch": branch,
        "test_package": tpackage,
        "test_class": tclass,
        "test_case": tcase,
        "test_config": tconfig
    }
    return url, query_params


def test_case_key(test: dict):
    return (
        test["test_run"]["test_package"],
        test["test_run"]["test_suite"],
        test["test_run"]["test_case"],
        test["test_run"]["test_config"],
    )


class FailedTests:
    """
    Helper object to group test case -> [test runs] from a flat list of [(test_run, suite_run)] dicts:
    1. get list of unique test names (keys), then
    2. for each test key get list of runs for this test
    The key is a tuple(package, suite, case, config)
    """
    def __init__(self, data):
        self.data = data

    def unique_test_cases(self, limit: int = None, threshold: int = None):
        keys = {}
        for item in self.data:
            k = test_case_key(item)
            if k not in keys:
                keys[k] = 0
            keys[k] = keys[k] + 1

        if threshold is not None:
            keys = {k: v for k, v in keys.items() if v >= threshold}
        return sorted(keys, key=keys.get, reverse=True)[:limit]

    def runs_for_test_case(self, key):
        return [x for x in self.data if test_case_key(x) == key]


@tests_app.command()
def failed(suite: str, branch: str, org: str = None, project: str = None, limit: int = None, threshold: int = None):
    """
    Prints out the list of test failures for given suite and branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param flag to show ignored
    TODO: use url links for builds if present
    """
    terec_org = value_or_env(org, "TEREC_ORG")
    terec_prj = value_or_env(project, "TEREC_PRJ")
    data = get_failed_tests(org, project, suite, branch)
    grouped_data = FailedTests(data)
    uniq_test_cases = grouped_data.unique_test_cases(limit=limit, threshold=threshold)
    # configure table
    title = f"Failed tests of {terec_org}/{terec_prj}/{suite} on branch {branch}"
    caption = f"Limit: {limit}, Threshold: {threshold}"
    table = Table(**typer_table_config(title, caption))
    table.add_column("package", justify="left")
    table.add_column("class(suite)", justify="left")
    table.add_column("test", justify="left")
    table.add_column("config", style="dim", justify="left")
    table.add_column("group", style="dim", justify="center")
    table.add_column("[red]Fail #[red]", justify="center", style="red")
    table.add_column("[red]Failed in[red]", justify="left", style="red")
    # print results
    for test_case in uniq_test_cases:
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
            " ".join(failed_runs_ids[:8]) + ("(...)" if len(failed_runs) > 8 else ""),
        )

    console = Console()
    console.print()
    console.print(table)


@tests_app.command()
def history(suite: str, branch: str, org: str = None, project: str = None, limit: int = None, threshold: int = None):
    """
    Prints out the list of tests that failed at least once given suite and branch.
    For each test it prints number of failures, skip and history of runs
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.
    TODO: add param flag to show ignored
    TODO: use url links for builds if present
    """
    terec_org = value_or_env(org, "TEREC_ORG")
    terec_prj = value_or_env(project, "TEREC_PRJ")
    # collect all failed tests
    with Timer("get-failed-tests"):
        data = get_failed_tests(org, project, suite, branch)
    grouped_data = FailedTests(data)
    uniq_test_cases = grouped_data.unique_test_cases(limit=limit, threshold=threshold)
    # collect history for all interesting tests [TODO: make it asynchttp]
    with Timer("collect-test-results"):
        calls = []
        for test_case in uniq_test_cases:
            tpackage, tsuite, tcase, tconfig = test_case
            url, params = get_test_history_api_call(org, project, suite, branch, tpackage, tsuite, tcase, tconfig)
            calls.append((test_case, url, params))

        tests_history = asyncio.run(collect_terec_rest_api_calls(calls))

    # configure table
    title = f"Test history of {terec_org}/{terec_prj}/{suite} on branch {branch}"
    caption = f"Limit: {limit}, Threshold: {threshold}"
    table = Table(**typer_table_config(title, caption))
    # configure columns
    table.add_column("package", justify="left")
    table.add_column("class(suite)", justify="left")
    table.add_column("test", justify="left")
    table.add_column("config", style="dim", justify="left")
    table.add_column("group", style="dim", justify="center")
    table.add_column("[green]Pass#[green]", justify="right", style="green")
    table.add_column("[red]Fail#[red]", justify="right", style="red")
    table.add_column("[yellow]Skip#[yellow]", justify="right", style="yellow")
    table.add_column("History", justify="left")
    # add rows
    for test_case in uniq_test_cases:
        package, suite, case, config = test_case
        history = sorted(tests_history[test_case], reverse=True, key=lambda x: x["suite_run"]["run_id"])

        t_group = next((x["test_run"]["test_group"] for x in history if x["test_run"]["test_group"] is not None), "---")
        history_stream = []
        pass_count, fail_count, skip_count = 0, 0, 0
        for r in history:
            r_id = r["suite_run"]["run_id"]
            if r["test_run"]["result"] == "PASS":
                pass_count += 1
                history_stream.append(f"[green]#{r_id}[green]")
            elif r["test_run"]["result"] == "SKIP":
                skip_count += 1
                history_stream.append(f"[yellow]#{r_id}[yellow]")
            elif r["test_run"]["result"] == "FAIL":
                fail_count += 1
                history_stream.append(f"[red]#{r_id}[red]")
        total_count = fail_count + pass_count + skip_count
        table.add_row(
            str(package),
            str(suite),
            str(case),
            str(config),
            str(t_group),
            " ".join([str(pass_count), ratio_str(pass_count, total_count)]),
            " ".join([str(fail_count), ratio_str(fail_count, total_count)]),
            str(skip_count),
            " ".join(history_stream),
        )

    console = Console()
    console.print()
    console.print(table)

