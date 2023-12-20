import asyncio
import sys

import typer

from codetiming import Timer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from terec.api.routers.results import TestCaseRunInfo
from terec.status_cli.util import (
    get_terec_rest_api,
    typer_table_config,
    ratio_str,
    collect_terec_rest_api_calls,
    TerecCallContext,
)

tests_app = typer.Typer()


def get_failed_tests(terec: TerecCallContext, suite: str, branch: str):
    # collect response from terec server
    url = f"{terec.url}/history/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/failed-tests"
    query_params = {"branch": branch, "user_req_id": terec.user_req_id}
    return get_terec_rest_api(url, query_params)


def get_suite_run_failed_tests(terec: TerecCallContext, suite: str, run_id: int):
    # collect response from terec server
    url = f"{terec.url}/tests/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/runs/{run_id}/tests"
    query_params = {"result": "FAIL"}
    return get_terec_rest_api(url, query_params)


def get_test_history_api_call(
    terec: TerecCallContext,
    suite: str,
    branch: str,
    tpackage: str,
    tclass: str,
    tcase: str,
    tconfig: str,
):
    # collect response from terec server
    url = f"{terec.url}/history/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/test-runs"
    query_params = {
        "branch": branch,
        "test_package": tpackage,
        "test_class": tclass,
        "test_case": tcase,
        "test_config": tconfig,
        "user_req_id": terec.user_req_id,
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
def failed(
    suite: str,
    branch: str,
    org: str = None,
    project: str = None,
    limit: int = None,
    threshold: int = None,
    fold: bool = False,
):
    """
    Prints out the list of test failures for given suite and branch.
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: add param flag to show ignored
    TODO: use url links for builds if present
    """
    terec = TerecCallContext.create(org, project)
    data = get_failed_tests(terec, suite, branch)
    grouped_data = FailedTests(data)
    uniq_test_cases = grouped_data.unique_test_cases(limit=limit, threshold=threshold)
    # configure table
    title = f"Failed tests of {terec.org}/{terec.prj}/{suite} on branch {branch}"
    caption = f"Limit: {limit}, Threshold: {threshold}"
    table = Table(**typer_table_config(title, caption))
    add_test_case_columns_to_table(table, fold)
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

        row_data = test_case_row_data(package, suite, case, config, fold)
        row_data += [
            str(t_group),
            f"{len(failed_runs)}",
            " ".join(failed_runs_ids[:8]) + ("(...)" if len(failed_runs) > 8 else ""),
        ]
        table.add_row(*row_data)

    console = Console()
    console.print()
    console.print(table)


def add_test_case_columns_to_table(table, fold: bool):
    if fold:
        table.add_column("package::class::test::config", justify="left", overflow="fold")
    else:
        table.add_column("package", justify="left")
        table.add_column("class(suite)", justify="left")
        table.add_column("test", justify="left")
        table.add_column("config", justify="left", style="dim")


def test_case_row_data(package, suite, case, config, fold: bool) -> list[str]:
    if fold:
        return [f"{package}::{suite}::{case}::{config}"]
    else:
        return [str(package), str(suite), str(case), str(config)]


# TODO: add param flag to show ignored
# TODO: use url links for builds if present
@tests_app.command()
def history(
    suite: str,
    branch: str,
    org: str = None,
    project: str = None,
    limit: int = None,
    threshold: int = None,
    fold: bool = False,
):
    """
    Prints out the list of tests that failed at least once given suite and branch.
    For each test it prints number of failures, skip and history of runs
    Requires TEREC_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.
    """
    terec = TerecCallContext.create(org, project)
    # collect all failed tests
    with Timer("get-failed-tests"):
        data = get_failed_tests(terec, suite, branch)
    grouped_data = FailedTests(data)
    uniq_test_cases = grouped_data.unique_test_cases(limit=limit, threshold=threshold)
    # collect history for all interesting tests [TODO: make it asynchttp]
    with Timer("collect-test-results"):
        calls = []
        for test_case in uniq_test_cases:
            tpackage, tsuite, tcase, tconfig = test_case
            url, params = get_test_history_api_call(
                terec,
                suite,
                branch,
                tpackage,
                tsuite,
                tcase,
                tconfig,
            )
            calls.append((test_case, url, params))

        tests_history = asyncio.run(collect_terec_rest_api_calls(calls))

    # configure table
    title = f"Test history of {terec.org}/{terec.prj}/{suite} on branch {branch}"
    caption = f"Limit: {limit}, Threshold: {threshold}"
    table = Table(**typer_table_config(title, caption))
    # configure columns
    add_test_case_columns_to_table(table, fold)
    table.add_column("group", style="dim", justify="center")
    table.add_column("[green]Pass#[green]", justify="right", style="green")
    table.add_column("[red]Fail#[red]", justify="right", style="red")
    table.add_column("[yellow]Skip#[yellow]", justify="right", style="yellow")
    table.add_column("History", justify="left")
    # add rows
    for test_case in uniq_test_cases:
        package, suite, case, config = test_case
        history = sorted(
            tests_history[test_case],
            reverse=True,
            key=lambda x: x["suite_run"]["run_id"],
        )

        t_group = next(
            (
                x["test_run"]["test_group"]
                for x in history
                if x["test_run"]["test_group"] is not None
            ),
            "---",
        )
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
        row_data = test_case_row_data(package, suite, case, config, fold)
        row_data += [
            str(t_group),
            " ".join([str(pass_count), ratio_str(pass_count, total_count)]),
            " ".join([str(fail_count), ratio_str(fail_count, total_count)]),
            str(skip_count),
            " ".join(history_stream),
        ]
        table.add_row(*row_data)

    console = Console()
    console.print()
    console.print(table)


def get_test_run_check(
    terec: TerecCallContext, suite: str, run_id: int, test_run: TestCaseRunInfo
):
    url = f"{terec.url}/history/orgs/{terec.org}/projects/{terec.prj}/suites/{suite}/test-run-check"
    q_params = {
        "run_id": run_id,
        "test_package": test_run.test_package,
        "test_class": test_run.test_suite,
        "test_case": test_run.test_case,
        "test_config": test_run.test_config,
    }
    return get_terec_rest_api(url, q_params)


@tests_app.command()
def regression_check(
    suite: str,
    branch: str,
    run_id: int = None,
    org: str = None,
    project: str = None,
    limit: int = typer.Option(16, help="number of past builds to use"),
):
    """
    Check suite run in terms of regression or known test failures.
    Takes given suite run and checks all failed tests against previous runs for same suite and branch.
    """
    # validate input
    terec = TerecCallContext.create(org, project)
    # TODO: get recent build if run_id not provided
    if not run_id:
        print("not implemented")
        return 0
    # collect all tests failed in this build
    console = Console()
    with Timer("get-failed-tests"):
        failed_tests = get_suite_run_failed_tests(terec, suite, run_id)
    if not failed_tests:
        console.print(
            f"[green]No regression[green]: no test failures for suite run {terec.org}/{terec.prj}/{suite}/{run_id}."
        )
        return 0
    # asynchronously check each failure
    console.print(
        f"Checking {len(failed_tests)} failed tests in suite run {terec.org}/{terec.prj}/{suite}/{run_id}."
    )
    # TODO: add --progress
    # TODO: make it asynchronous
    # TODO: use provided limit
    new_failures = []
    with Progress(console=Console(file=sys.stderr)) as progress:
        task = progress.add_task("checking failed tests", total=len(failed_tests))
        for test_case in failed_tests:
            info = TestCaseRunInfo(**test_case)
            console.print()
            check = get_test_run_check(terec, suite, run_id, info)
            if check["is_known_failure"] == False:
                new_failures.append(check)
            progress.update(task, advance=1)
    # summary
    if not new_failures:
        console.print("[green]No regression[green]: no new test failures.")
        return 0

    console.print("[red]Regression detected[red]")
    console.print(
        f"{len(new_failures)}/{len(failed_tests)} are new (not known yet) test failures."
    )
    # print details
    for f in new_failures:
        test_case = TestCaseRunInfo(**f["test_case"])
        console.print(str(test_case))
        console.print(f["summary"])
        console.print(f["message"])
