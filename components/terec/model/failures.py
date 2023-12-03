from cassandra.concurrent import execute_concurrent_with_args
from cassandra.cqlengine.connection import get_session

from terec.model.results import TestSuiteRun, TestCaseRun


def load_suite_branch_runs(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32
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


def get_failed_tests_for_suite_runs(
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
