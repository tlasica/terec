from cassandra.concurrent import execute_concurrent_with_args
from cassandra.cqlengine.connection import get_session

from terec.model.results import TestSuiteRun, TestCaseRun


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
    # collect and combine results
    rows = []
    errors = []
    for success, res in results:
        if success:
            rows += res  # result will be a list of rows
        else:
            errors.append(res)  # result will be an Exception
    # raise if any errors hit
    if errors:
        raise Exception(
            f"{len(errors)}/{len(params)} queries failed. Example failure: {str(errors[0])}"
        )
    # convert each item to TestCaseRun model object
    tests = [TestCaseRun(**r) for r in rows]
    tests.sort(reverse=True, key=lambda x: x.test_case_run_id_tuple())
    return tests
