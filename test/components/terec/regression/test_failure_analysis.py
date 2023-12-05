from generator import generate_suite_with_test_runs
from terec.regression.failure_analysis import TestCaseRunFailureAnalyser


class TestFailureAnalyser:
    def test_it_does_not_crash(self, cassandra_model, test_project):
        # given some generated data with failed tests
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            test_project.org, test_project.name
        )
        # when we run analyser
        the_test = next((x for x in test_runs if x.result == "FAIL"))
        analyzer = TestCaseRunFailureAnalyser(the_test, branch="main")
        analyzer.check()
        # it does not crash....
        assert analyzer.num_test_runs_checked() > 0
