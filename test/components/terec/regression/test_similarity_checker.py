from faker import Faker

from .text_samples import sample_npe_stack_trace, sample_npe_stack_trace_with_line_changes, different_npe_stack_trace
from generator import ResultsGenerator
from terec.model.results import TestCaseRun
from terec.regression.similarity_checker import SimilarityChecker


class TestSimilarityChecker:

    fake = Faker()
    gen = ResultsGenerator()

    def random_test_case_run(self):
        run = TestCaseRun()
        run.org = "some-org"
        run.project = "some-prj"
        run.suite = "some-suite"
        run.error_details = self.gen.random_output(1)
        run.error_stacktrace = self.gen.random_output(10)
        return run

    def test_similarity_check_on_same_object(self):
        test_run = self.random_test_case_run()
        checker = SimilarityChecker(test_run)
        assert checker.is_similar(test_run)

    def test_similarity_check_on_completely_different_object(self):
        test_run = self.random_test_case_run()
        checker = SimilarityChecker(test_run)
        diff_run = self.random_test_case_run()
        assert not checker.is_similar(diff_run)

    def test_similarity_check_is_none_if_no_stacktrace(self):
        test_run = self.random_test_case_run()
        checker = SimilarityChecker(test_run)
        diff_run = self.random_test_case_run()
        diff_run.error_stacktrace = ""
        diff_run.error_details = test_run.error_details
        assert checker.is_similar(diff_run) is None

    def test_similarity_check_on_a_slightly_changed_stacktrace(self):
        test_run = self.random_test_case_run()
        test_run.error_stacktrace = sample_npe_stack_trace
        checker = SimilarityChecker(test_run)
        diff_run = self.random_test_case_run()
        diff_run.error_details = test_run.error_details
        diff_run.error_stacktrace = sample_npe_stack_trace_with_line_changes
        assert checker.is_similar(diff_run)

    def test_similarity_check_on_similar_but_different_stacktrace(self):
        test_run = self.random_test_case_run()
        test_run.error_stacktrace = sample_npe_stack_trace
        checker = SimilarityChecker(test_run)
        diff_run = self.random_test_case_run()
        diff_run.error_details = test_run.error_details
        diff_run.error_stacktrace = different_npe_stack_trace
        assert not checker.is_similar(diff_run)
