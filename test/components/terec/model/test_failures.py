from generator import ResultsGenerator
from conftest import random_name
from terec.model.failures import load_failed_tests_for_suite_runs


def test_get_failed_tests_for_suite_runs(cassandra_model, test_project):
    # given some runs
    gen = ResultsGenerator()
    suite_name = random_name("suite")
    suite = gen.suite(test_project.org, test_project.name, suite_name)
    runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
    for r in runs:
        gen.test_case_runs(r)
    # when we collect failed tests
    failed_tests = load_failed_tests_for_suite_runs(runs)
    # then we get expected number of failures
    expected_count = sum([x.fail_count for x in runs])
    assert len(failed_tests) == expected_count
    # TODO: check if properly sorted
