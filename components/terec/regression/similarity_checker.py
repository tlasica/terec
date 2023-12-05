import Levenshtein
import re

from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from terec.model.results import TestCaseRun


def levenshtein_sim_ratio(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    normalized_distance = distance / max(len(str1), len(str2))
    similarity_ratio = 1 - normalized_distance
    return similarity_ratio


def cosine_sim_ratio(str1, str2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([str1.lower(), str2.lower()])
    # Compute cosine similarity between documents
    cosine_similarity_matrix = cosine_similarity(tfidf_matrix)
    # Extract the similarity score from the matrix
    cosine_similarity_score = cosine_similarity_matrix[0, 1]
    # Normalize to obtain similarity ratio in the range of 0 to 1
    return (cosine_similarity_score + 1) / 2


class SimilarityChecker:
    """
    SimilarityChecker provides logic to validate if a failed test case run
    is similar to some other - already known - test case run (also failed).
    It uses fields such as error_details or error_stacktrace as well as stderr/stdout.
    """

    LEVENSHTEIN_RATIO_THRESHOLD = 0.90
    COSINE_SIM_RATIO_THRESHOLD = 0.97

    def __init__(self, test_case_run: TestCaseRun):
        self.test_case_run = test_case_run

    def is_similar(self, other: TestCaseRun):
        sim_error_details = self.is_error_details_similar(self.test_case_run.error_details, other.error_details)
        sim_stack_trace = self.is_stacktrace_similar(self.test_case_run.error_stacktrace, other.error_stacktrace)
        if sim_stack_trace is not None and sim_error_details in [True, None]:
            return sim_stack_trace
        sim_stdout = self.is_out_stream_similar(self.test_case_run.stdout, other.stdout)
        sim_stderr = self.is_out_stream_similar(self.test_case_run.stdout, other.stdout)
        if sim_stack_trace is None or (sim_stderr is None and sim_stdout is None):
            return None
        return sim_stderr and sim_stdout

    def is_text_similar(self, this_value: str, other_value: str):
        if not this_value or not other_value:
            return None
        if levenshtein_sim_ratio(this_value, other_value) < self.LEVENSHTEIN_RATIO_THRESHOLD:
            return False
        if cosine_sim_ratio(this_value, other_value) < self.COSINE_SIM_RATIO_THRESHOLD:
            return False
        return True

    def is_error_details_similar(self, error_1: str, error_2: str) -> bool:
        return self.is_text_similar(error_1, error_2)

    def is_stacktrace_similar(self, stacktrace_1: str, stacktrace_2: str) -> bool | None:
        """
        Comparing two stack traces is tricky because we should cover following:
        - line numbers change related to code structure changes like new additions
        - flow changes e.g. similar stacktrace but with different start point
        - same stacktrace but on different objects e.g. different names

        We will take following approach:
        1. both stacktraces should have similar line structure as it reflects the code flow
        2. lines should be similar, but it is not required to be identical
        """
        if not stacktrace_1 or not stacktrace_2:
            return None
        st_1_lines = stacktrace_1.splitlines(keepends=False)
        st_2_lines = stacktrace_2.splitlines(keepends=False)
        if len(st_1_lines) != len(st_2_lines):
            return False
        for a, b in zip(st_1_lines, st_2_lines):
            if a == b:
                continue
            a = self.normalize_stack_trace_line(a)
            b = self.normalize_stack_trace_line(b)
            if not self.is_text_similar(a, b):
                return False
        return True

    def normalize_stack_trace_line(self, stack_trace_line):
        # Remove line numbers in Java-style stack traces
        stack_trace_line = re.sub(r"(:\d+)", ":X", stack_trace_line)
        # Normalize file paths
        stack_trace_line = re.sub(r"([a-zA-Z]:)?\\|/", "/", stack_trace_line)
        # Replace memory addresses
        stack_trace_line = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", stack_trace_line)
        return stack_trace_line

    def is_out_stream_similar(self, out_1: str, out_2: str) -> bool | None:
        """
        Comparing two output streams is tricky due to
        1. dates or numbers changed
        2. potentially new log lines
        So we need to normalize it first and then measure similarity
        """
        if not out_1 or not out_2:
            return None
        matcher = SequenceMatcher(a=out_1, b=out_2)
        return matcher.ratio() >= 0.95
