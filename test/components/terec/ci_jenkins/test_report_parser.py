from _pytest.fixtures import fixture

from terec.api.routers.results import TestCaseRunInfo
from terec.ci_jenkins.report_parser import (
    split_fq_class_name,
    split_case_name_with_config,
    parse_jenkins_report_suite,
)
from terec.model.results import TestCaseRunStatus
from .sample_data.build_test_report import sample_build_test_report_suite


def test_split_fq_class_name():
    assert (None, "Clazz") == split_fq_class_name("Clazz")
    assert ("a", "Clazz") == split_fq_class_name("a.Clazz")
    assert ("org.example", "Clazz") == split_fq_class_name("org.example.Clazz")
    assert ("org.example", "Clazz-config") == split_fq_class_name(
        "org.example.Clazz-config"
    )


def test_split_case_name_with_config():
    assert ("case", None) == split_case_name_with_config("case")
    assert ("case", "config") == split_case_name_with_config("case-config")
    assert ("case", "config-2") == split_case_name_with_config("case-config-2")
    assert ("the_case", "config-2") == split_case_name_with_config("the_case-config-2")


class TestParseReportSuite:
    @fixture(scope="session")
    def suite_info(self) -> dict[str:TestCaseRunInfo]:
        suite_info = {}
        for s in parse_jenkins_report_suite(sample_build_test_report_suite()):
            key = f"{s.test_case}/{s.test_config}"
            suite_info[key] = s
        return suite_info

    def test_parser_should_find_all_items(self, suite_info):
        expected_len = len([x for x in sample_build_test_report_suite()["cases"]])
        assert (
            len(suite_info) == expected_len
        ), f"Expected {expected_len} cases but got: {suite_info.keys()}"

    def test_parser_should_handle_skipped_case(self, suite_info):
        test = suite_info.get("skipped_test/#", None)
        assert test is not None
        assert test.result == TestCaseRunStatus.SKIP
        assert test.skip_details == "not applicable"

    def test_parser_should_set_error_details(self, suite_info):
        test = suite_info.get("failed_test/#", None)
        assert test is not None
        assert test.result == TestCaseRunStatus.FAIL
        assert test.error_details == "error details example"
        assert test.error_stacktrace == "stack trace example"
        assert test.stdout == "stdout example"
        assert test.stderr == "stderr example"

    def test_parser_should_set_timestamp(self, suite_info):
        import datetime

        for case in suite_info.values():
            assert case.tstamp is not None
            assert case.tstamp == datetime.datetime(2023, 10, 26, 14, 1, 50)

    def test_parser_should_set_status_for_failed_case(self, suite_info):
        test = suite_info.get("failed_test/#", None)
        assert test is not None
        assert test.result == TestCaseRunStatus.FAIL
        test = suite_info.get("regression_test/#", None)
        assert test is not None
        assert test.result == TestCaseRunStatus.FAIL

    def test_parser_should_set_status_for_passed_case(self, suite_info):
        tests = [x for x in suite_info.values() if x.test_case == "multiColumn"]
        assert tests
        for t in tests:
            assert t.result == TestCaseRunStatus.PASS

    def test_parser_should_handle_duplicate_test_case_names(self, suite_info):
        pass

    def test_parser_should_set_default_config(self, suite_info):
        test = suite_info.get("failed_test/#", None)
        assert test is not None
        assert test.test_config == "#"
