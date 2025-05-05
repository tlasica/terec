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

    def __init__(
        self,
        failed_test: TestCaseRun,
    ):
        self.failed_test = failed_test
        self.messages = []
        self.similar_failures = []
        self.suite_runs_to_check = []
        self.test_runs_to_check = []
        self.depth = None
        self.check_suite = None
        self.check_branch = None

    def full_suite_name(self):
        return f"{self.failed_test.org}/{self.failed_test.project}/{self.check_suite}::{self.check_branch}"

    def message(self):
        return "\n".join(self.messages)

    def add_msg(self, msg: str):
        logger.info(msg)
        self.messages.append(msg)

    def check_regression(self, depth: int = 16):
        """
        Check if failed_test case failure is a regression vs history of the same suite on the same branch.
        In this case suite and branch will be same as the failed tests.
        And only builds with run_id < failed_test.run_id will be checked.
        """
        self.check_suite = self.failed_test.suite
        self.check_branch = self.failed_test.branch
        before_run = self.failed_test.run_id
        self.add_msg(
            f"Checking regression on {self.check_suite}::{self.check_branch} before run {before_run}"
        )
        self._check(before_run_id=before_run, depth=depth)

    def check_vs_upstream(self, suite: str, branch: str, depth: int = 16):
        """
        Check if failed_test case failure is a known failure vs some upstream branch runs.
        In this case suite and branch need to be provided.
        All builds on upstream (even recent ones, run after failed_test) will be checked.
        """
        self.check_suite = suite
        self.check_branch = branch
        self.add_msg(f"Checking regression vs upstream {suite}::{branch}")
        self._check(before_run_id=None, depth=depth)

    def _check(self, before_run_id: int = None, depth: int = 16):
        self.add_msg(f"Using depth of {depth}")
        self.depth = depth
        # collect relevant builds to check
        run_filter = None
        if before_run_id:
            self.add_msg(f"Using only suite runs with id < {before_run_id}.")
            run_filter = lambda x: x.run_id < before_run_id
        self.collect_relevant_builds(run_filter)
        if not self.suite_runs_to_check:
            self.add_msg("No suite runs for checking found.")
            return
        # collect all the test runs of failed tests in the interesting suite runs
        self.collect_test_runs()
        if not self.test_runs_to_check:
            self.add_msg(
                f"Got {len(self.suite_runs_to_check)} suite runs but no test runs for the test under check."
            )
            return
        # and analyze them
        self.find_similar_test_runs()

    def collect_relevant_builds(self, run_filter):
        suite_runs = load_suite_branch_runs(
            self.failed_test.org,
            self.failed_test.project,
            self.check_suite,
            self.check_branch,
            limit=self.depth,
        )
        self.suite_runs_to_check = [
            x for x in suite_runs if run_filter is None or run_filter(x)
        ]

    def is_same_run_as_failed_test(self, run: TestSuiteRun) -> bool:
        return (
            run.project == self.failed_test.project
            and run.org == self.failed_test.org
            and run.suite == self.failed_test.suite
            and run.run_id == self.failed_test.run_id
        )

    def collect_test_runs(self):
        suite_runs_ids = [x.run_id for x in self.suite_runs_to_check]
        test_runs = load_test_case_runs(
            org_name=self.failed_test.org,
            project_name=self.failed_test.project,
            suite_name=self.check_suite,
            branch=self.check_branch,
            runs=suite_runs_ids,
            test_package=self.failed_test.test_package,
            test_class=self.failed_test.test_suite,
            test_case=self.failed_test.test_case,
        )
        logger.info(
            "Found {} test runs to check for test {}.",
            len(test_runs),
            f"{str(self.failed_test)}",
        )
        if not test_runs:
            self.message += f"Cannot check: no runs for the test under check for suite {self.full_suite_name()}::{self.check_branch}."
            self.message += f"Builds considered: {suite_runs_ids}."
        self.test_runs_to_check = test_runs

    def find_similar_test_runs(self):
        sim_checker = SimilarityChecker(self.failed_test)
        for other in self.test_runs_to_check:
            if other.result == "FAIL":
                logger.info(f"checking {other}")
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
