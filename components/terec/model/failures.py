from cassandra import query
from cassandra.concurrent import execute_concurrent_with_args
from cassandra.cqlengine.connection import get_session

from terec.model.results import TestSuiteRun, TestCaseRun


def get_failed_tests_for_suite_runs(runs: list[TestSuiteRun], session=None) -> list[TestCaseRun]:
    """
    Loads all test failures for given list of runs (builds).
    Session can be explicitly provided or will be taken from cqlengine.
    To make things more performant we will use concurrent queries.
    """
    session = session or get_session()
    # prepare statement
    select_cql = (f"SELECT * FROM {TestCaseRun.column_family_name(include_keyspace=True)} "
                  f"WHERE org=? AND project=? AND suite=? AND run_id=? AND result=?")
    stmt = session.prepare(select_cql)
    # create list of parameters for the queries
    params = [(r.org,r. project, r.suite, r.run_id, "FAIL") for r in runs]
    # run the query
    concurrency = 7
    results = execute_concurrent_with_args(session, stmt, params, concurrency=concurrency)
    # collect and combine results
    rows = []
    errors = []
    for (success, res) in results:
        if not success:
            errors.append(res) # result will be an Exception
        else:
            rows += res # result will be a list of rows
    if errors:
        raise Exception(f"{len(errors)}/{len(params)} queries failed. Example failure: {str(errors[0])}")
    return rows
