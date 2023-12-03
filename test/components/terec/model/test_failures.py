from generator import ResultsGenerator
from conftest import random_name
from terec.model.failures import load_failed_tests_for_suite_runs, load_test_case_runs
from terec.model.results import TestCaseRun


def generate_suite_with_test_runs(org, project):
    gen = ResultsGenerator()
    suite_name = random_name("suite")
    suite = gen.suite(org, project, suite_name)
    suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
    test_runs = []
    for r in suite_runs:
        test_runs += gen.test_case_runs(r)
    return suite, suite_runs, test_runs


def test_get_failed_tests_for_suite_runs(cassandra_model, test_project):
    # given some runs
    suite, suite_runs, test_runs = generate_suite_with_test_runs(test_project.org, test_project.name)
    # when we collect failed tests
    failed_tests = load_failed_tests_for_suite_runs(suite_runs)
    # then we get expected number of failures
    expected_count = sum([x.fail_count for x in suite_runs])
    assert len(failed_tests) == expected_count
    # TODO: check if properly sorted


def test_load_test_case_runs_without_config(cassandra_model, test_project):
    # given some runs
    suite, suite_runs, test_runs = generate_suite_with_test_runs(test_project.org, test_project.name)
    # when we load all runs of selected test
    the_test: TestCaseRun = test_runs[0]
    loaded_test_runs = load_test_case_runs(
        test_project.org, test_project.name, suite.suite,
        [r.run_id for r in suite_runs],
        test_package=the_test.test_package,
        test_class=the_test.test_suite,
        test_case=the_test.test_case,
    )
    # then we got from database expected
    generated_test_runs = [x for x in test_runs if the_test.is_same_test_case(x)]
    assert len(loaded_test_runs) == len(generated_test_runs)


def test_load_test_case_runs_with_config(cassandra_model, test_project):
    # given some runs
    suite, suite_runs, test_runs = generate_suite_with_test_runs(test_project.org, test_project.name)
    # when we load all runs of selected test
    the_test: TestCaseRun = test_runs[0]
    loaded_test_runs = load_test_case_runs(
        test_project.org, test_project.name, suite.suite,
        [r.run_id for r in suite_runs],
        test_package=the_test.test_package,
        test_class=the_test.test_suite,
        test_case=the_test.test_case,
        test_config=the_test.test_config,
    )
    # then we got from database expected
    generated_test_runs = [x for x in test_runs if the_test.is_same_test_case_and_config(x)]
    assert len(loaded_test_runs) == len(generated_test_runs)


def test_load_test_case_runs_with_result(cassandra_model, test_project):
    # given some runs
    suite, suite_runs, test_runs = generate_suite_with_test_runs(test_project.org, test_project.name)
    the_test = next((x for x in test_runs if x.result == "FAIL"))
    # when we load all runs of selected test
    loaded_test_runs = load_test_case_runs(
        test_project.org, test_project.name, suite.suite,
        [r.run_id for r in suite_runs],
        test_package=the_test.test_package,
        test_class=the_test.test_suite,
        test_case=the_test.test_case,
        test_config=the_test.test_config,
        result="FAIL"
    )
    # then we got from database expected
    generated_test_runs = [x for x in test_runs if the_test.is_same_test_case_and_config(x) and x.result == "FAIL"]
    assert len(loaded_test_runs) == len(generated_test_runs)
