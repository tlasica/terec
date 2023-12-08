from cassandra.concurrent import execute_concurrent_with_args
from cassandra.cqlengine.connection import get_session

from terec.model.results import TestSuiteRun, TestCaseRun


def load_suite_branch_runs(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
) -> list[TestSuiteRun]:
    # collect runs results
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
    }
    if branch:
        query_params["branch"] = branch
    runs = TestSuiteRun.objects(**query_params).limit(limit)
    return runs


def load_failed_tests_for_suite_runs(
    runs: list[TestSuiteRun], session=None
) -> list[TestCaseRun]:
    """
    Loads all test failures for given list of runs (builds).
    Session can be explicitly provided or will be taken from cqlengine.
    To make things more performant we will use concurrent queries.
    """
    session = session or get_session()
    # prepare statement
    select_cql = (
        f"SELECT * FROM {TestCaseRun.column_family_name(include_keyspace=True)} "
        f"WHERE org=? AND project=? AND suite=? AND run_id=? AND result=?"
    )
    stmt = session.prepare(select_cql)
    # create list of parameters for the queries
    params = [(r.org, r.project, r.suite, r.run_id, "FAIL") for r in runs]
    # run the query
    concurrency = 32
    results = execute_concurrent_with_args(
        session, stmt, params, concurrency=concurrency
    )
    # check for errors
    errors = [error for ok, error in results if not ok]
    if errors:
        raise Exception(
            f"{len(errors)}/{len(params)} queries failed. Example failure: {str(errors[0])}"
        )
    # collect and combine results
    tests = []
    for success, rows in results:
        if success:
            tests += [TestCaseRun(**r) for r in rows]
    tests.sort(reverse=True, key=lambda x: x.test_case_run_id_tuple())
    return tests


def load_test_case_runs(
    org_name: str,
    project_name: str,
    suite_name: str,
    runs: list[int],
    test_package: str,
    test_class: str,
    test_case: str,
    test_config: str | None = None,
    result: str | None = None,
    limit: int = 10000,
) -> list[TestCaseRun]:
    """
    Returns all runs of given test case in given list of suite runs.
    test_config parameter is optional - if None then all configurations will be returned.
    result is also optional: if provided only test runs with given result are returned.
    TODO: what is more efficient: run_id IN or maybe execute concurrent?
    TODO: what about order?
    """
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
        "run_id__in": runs,
        "test_package": test_package,
    }
    if test_class:
        query_params["test_suite"] = test_class
    if test_case:
        query_params["test_case"] = test_case
    if test_config:
        query_params["test_config"] = test_config
    # collect failures for given runs history
    test_runs = TestCaseRun.objects().filter(**query_params).limit(limit).all()
    # filter by result
    # TODO: it is not allowed to combine IN with index check => we need execute concurrent
    return [x for x in test_runs if (not result) or (x.result == result)]
