import pytest

from terec.model.results import TestSuiteRun
from .text_samples import sample_npe_stack_trace

from conftest import random_name
from generator import ResultsGenerator
from terec.regression.failure_analysis import TestCaseRunFailureAnalyser


class TestFailureAnalyser:
    TEST_FAIL = {
        "result": "FAIL",
        "error_details": "error happened",
        "error_stacktrace": sample_npe_stack_trace,
    }

    TEST_PASS = {
        "result": "PASS",
    }

    @pytest.fixture()
    def gen_with_suite_runs(self, cassandra_model, test_project):
        suite_name = random_name("suite")
        gen = ResultsGenerator(num_tests=4)
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 5)]
        assert len(suite_runs) == 4
        assert suite_runs[0].run_id == 1 and suite_runs[-1].run_id == 4
        return gen

    def test_check_regression_with_same_failure(self, gen_with_suite_runs):
        # given a history of test runs with some failure FPPF
        gen = gen_with_suite_runs
        case_template = gen.test_case_template()
        history = [
            gen.test_case_run(gen.get_suite_run(1), case_template, self.TEST_FAIL),
            gen.test_case_run(gen.get_suite_run(2), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(3), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(4), case_template, self.TEST_FAIL),
        ]
        # when we analyze last failure
        failed_test = history[-1]
        analyzer = TestCaseRunFailureAnalyser(failed_test)
        analyzer.check_regression(depth=8)
        # then it analyzed all 3 previous runs
        assert analyzer.num_test_runs_checked() == len(history) - 1
        # and found one similar
        assert analyzer.is_known_failure()
        assert len(analyzer.similar_failures) == 1
        assert analyzer.similar_failures[0].run_id == 1

    def test_check_regression_with_new_failure(self, gen_with_suite_runs):
        # given a history of test runs with some failure FPPF
        gen = gen_with_suite_runs
        case_template = gen.test_case_template()
        history = [
            gen.test_case_run(gen.get_suite_run(1), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(2), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(3), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(4), case_template, self.TEST_FAIL),
        ]
        # when we analyze last failure
        failed_test = history[-1]
        analyzer = TestCaseRunFailureAnalyser(failed_test)
        analyzer.check_regression(depth=8)
        # then it analyzed all 3 previous runs
        assert analyzer.num_test_runs_checked() == len(history) - 1
        # and found no similar tests
        assert not analyzer.is_known_failure()
        assert not analyzer.similar_failures
        assert analyzer.num_test_runs_pass() == len(history) - 1

    def test_check_regression_with_different_failure(self, gen_with_suite_runs):
        # given a history of test runs with some failure FPPF
        gen = gen_with_suite_runs
        case_template = gen.test_case_template()
        history = [
            gen.test_case_run(
                gen.get_suite_run(1),
                case_template,
                self.TEST_FAIL | {"error_details": "different case"},
            ),
            gen.test_case_run(gen.get_suite_run(2), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(3), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(4), case_template, self.TEST_FAIL),
        ]
        # when we analyze last failure
        failed_test = history[-1]
        analyzer = TestCaseRunFailureAnalyser(failed_test)
        analyzer.check_regression(depth=8)
        # then it analyzed all 3 previous runs
        assert analyzer.num_test_runs_checked() == len(history) - 1
        # and found one similar
        assert not analyzer.is_known_failure()
        assert not analyzer.similar_failures
        assert analyzer.num_test_runs_pass() == 2
        assert analyzer.num_test_runs_fail() == 1
        assert analyzer.num_test_runs_fail_different_way() == 1
        assert analyzer.num_test_runs_fail_same_way() == 0

    def test_check_regression_vs_upstream(self, gen_with_suite_runs):
        # given a history of test runs with some failure FPPF
        gen = gen_with_suite_runs
        case_template = gen.test_case_template()
        main_history = [
            gen.test_case_run(gen.get_suite_run(1), case_template, self.TEST_FAIL),
            gen.test_case_run(gen.get_suite_run(2), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(3), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(4), case_template, self.TEST_FAIL),
        ]
        # and a failed run on some different branch / different suite
        main_suite_run: TestSuiteRun = gen.get_suite_run(1)
        ci = gen.suite(main_suite_run.org, main_suite_run.project, random_name("ci"))
        ci_run = gen.suite_run(ci, "my-branch", 5)
        failed_test = gen.test_case_run(ci_run, case_template, self.TEST_FAIL)
        # when we analyze last failure
        analyzer = TestCaseRunFailureAnalyser(failed_test)
        analyzer.check_vs_upstream(main_suite_run.suite, main_suite_run.branch, depth=8)
        # then it analyzed all 4 runs on main
        assert analyzer.num_test_runs_checked() == len(main_history)
        # and found one similar
        assert analyzer.is_known_failure()
        assert len(analyzer.similar_failures) == 2
        assert {x.run_id for x in analyzer.similar_failures} == {1, 4}
