from loguru import logger

from terec.model.failures import load_suite_branch_runs, load_test_case_runs
from terec.model.results import TestCaseRun, TestSuiteRun
from terec.regression.similarity_checker import SimilarityChecker


class TestCaseRunFailureAnalyser:
    """
    Allows to search for history of failures related to some test case run failure.
    Analysis can be done against any workflow/branch : same as the failure or different,
    but it is always done against same test case (package + class + case name).
    As we have multiple test configurations the result of the analysis is always
    organized into a map from configuration to some history.
    """

    __test__ = False

    def __init__(self, failed_test: TestCaseRun, branch: str, org: str=None, project: str=None, suite: str=None):
        self.failed_test = failed_test
        self.org = org or failed_test.org
        self.project = project or failed_test.project
        self.suite = suite or failed_test.suite
        self.branch = branch
        self.message = None
        self.similar_failures = []
        self.suite_runs_to_check = []
        self.test_runs_to_check = []

    def full_suite_name(self):
        return f"{self.org}/{self.project}/{self.suite}"

    def check(self):
        # collect relevant builds to check
        self.collect_relevant_builds()
        if not self.suite_runs_to_check:
            return
        # collect all the test runs of failed tests in the interesting suite runs
        self.collect_test_runs()
        if not self.test_runs_to_check:
            return
        # and analyze them
        self.find_similar_test_runs()

    def collect_relevant_builds(self):
        suite_runs = load_suite_branch_runs(self.org, self.project, self.suite, self.branch)
        if not suite_runs:
            self.message = f"Cannot check: no suite runs on branch {self.branch} for suite {self.full_suite_name()}."
        self.suite_runs_to_check = [x for x in suite_runs if not self.is_same_run_as_failed_test(x)]

    def is_same_run_as_failed_test(self, run: TestSuiteRun) -> bool:
        return (run.project == self.failed_test.project
                and run.org == self.failed_test.org
                and run.suite == self.failed_test.suite
                and run.run_id == self.failed_test.run_id)

    def collect_test_runs(self):
        suite_runs_ids = [x.run_id for x in self.suite_runs_to_check]
        test_runs = load_test_case_runs(
            org_name=self.org,
            project_name=self.project,
            suite_name=self.suite,
            runs=suite_runs_ids,
            test_package=self.failed_test.test_package,
            test_class=self.failed_test.test_suite,
            test_case=self.failed_test.test_case,
        )
        logger.info("Found {} test runs to check for test {}.", len(test_runs), f"{str(self.failed_test)}")
        if not test_runs:
            self.message += f"Cannot check: no runs for the test under check on branch {self.branch} for suite {self.full_suite_name()}."
            self.message += f"Builds considered: {suite_runs_ids}."
        self.test_runs_to_check = test_runs

    def find_similar_test_runs(self):
        sim_checker = SimilarityChecker(self.failed_test)
        for other in self.test_runs_to_check:
            if other.result == "FAIL":
                if sim_checker.is_similar(other):
                    self.similar_failures.append(other)
        return self.similar_failures

    def is_known_failure(self):
        if not self.test_runs_to_check:
            return None
        return len(self.similar_failures) > 0

    def num_test_runs_checked(self) -> int:
        return len(self.test_runs_to_check)

    def num_test_runs_fail(self) -> int:
        return len(list(self.test_runs_with_result("FAIL")))

    def num_test_runs_pass(self) -> int:
        return len(list(self.test_runs_with_result("PASS")))

    def num_test_runs_skip(self) -> int:
        return len(list(self.test_runs_with_result("SKIP")))

    def num_test_runs_fail_same_way(self) -> int:
        return len(self.similar_failures)

    def num_test_runs_fail_different_way(self) -> int:
        return self.num_test_runs_fail() - len(self.similar_failures)

    def test_runs_with_result(self, result):
        return (x for x in self.test_runs_to_check if x.result == result)
