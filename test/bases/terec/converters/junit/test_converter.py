import pytest
from terec.converters.junit.converter import JunitXmlConverter
from terec.api.routers.results import TestCaseRunStatus, TestSuiteRunStatus


@pytest.fixture
def sample_pytest_junit_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="pytest" tests="4" failures="1" errors="0" skipped="1" time="0.123">
        <testcase classname="test.module" name="test_passed" time="0.001" />
        <testcase classname="test.module" name="test_failed" time="0.002">
            <failure message="AssertionError">assert 1 == 2</failure>
        </testcase>
        <testcase classname="test.module" name="test_skipped" time="0.000">
            <skipped type="pytest.skip" message="skip reason" />
        </testcase>
        <testcase classname="test.module" name="test_passed_2" time="0.003" />
    </testsuite>
</testsuites>
"""


def test_junit_converter_parses_suites_and_cases(sample_pytest_junit_xml):
    junit_converter = JunitXmlConverter(sample_pytest_junit_xml)
    suite_runs = junit_converter.get_suite_runs()
    assert len(suite_runs) == 1
    suite = suite_runs[0]
    assert suite.suite == "pytest"
    assert suite.total_count == 4
    assert suite.fail_count == 1
    assert suite.skip_count == 1
    assert suite.pass_count == 2
    assert suite.status == TestSuiteRunStatus.FAILURE

    test_cases = junit_converter.get_test_cases_for_suite("pytest")
    assert len(test_cases) == 4
    cases_by_name = {case.test_case: case for case in test_cases}
    failed_case = cases_by_name["test_failed"]
    assert cases_by_name["test_passed"].result == TestCaseRunStatus.PASS
    assert cases_by_name["test_passed_2"].result == TestCaseRunStatus.PASS
    assert failed_case.result == TestCaseRunStatus.FAIL
    # error_details should be the message attribute
    assert failed_case.error_details == "AssertionError"
    # error_stacktrace should be the content of <failure>
    assert failed_case.error_stacktrace.strip() == "assert 1 == 2"
    # No stdout/stderr in this XML, should be None
    for case in cases_by_name.values():
        assert case.stdout is None
        assert case.stderr is None
    assert cases_by_name["test_skipped"].result == TestCaseRunStatus.SKIP
    assert cases_by_name["test_skipped"].skip_details is not None


def test_junit_converter_parses_system_out_err_plain_multiline():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="plain_output_suite" tests="1" failures="0" errors="0" skipped="0" time="0.01">
        <testcase classname="mod" name="plain_multiline" time="0.001">
            <system-out>
First line
Second line
Third line
            </system-out>
            <system-err>
Error line 1
Error line 2
            </system-err>
        </testcase>
    </testsuite>
</testsuites>
"""
    junit_converter = JunitXmlConverter(xml)
    test_cases = junit_converter.get_test_cases_for_suite("plain_output_suite")
    assert len(test_cases) == 1
    case = test_cases[0]
    # Strip leading/trailing whitespace for comparison
    assert case.stdout.strip() == "First line\nSecond line\nThird line"
    assert case.stderr.strip() == "Error line 1\nError line 2"


def test_junit_converter_parses_system_out_err():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="output_suite" tests="2" failures="0" errors="0" skipped="0" time="0.01">
        <testcase classname="mod" name="case_with_output" time="0.001">
            <system-out><![CDATA[First line\nSecond line\nThird line]]></system-out>
            <system-err><![CDATA[Error line 1\nError line 2]]></system-err>
        </testcase>
        <testcase classname="mod" name="case_without_output" time="0.002" />
    </testsuite>
</testsuites>
"""
    junit_converter = JunitXmlConverter(xml)
    test_cases = junit_converter.get_test_cases_for_suite("output_suite")
    assert len(test_cases) == 2
    by_name = {c.test_case: c for c in test_cases}
    case_with_output = by_name["case_with_output"]
    case_without_output = by_name["case_without_output"]
    assert case_with_output.stdout == "First line\nSecond line\nThird line"
    assert case_with_output.stderr == "Error line 1\nError line 2"
    # Explicitly check None when not present
    assert case_without_output.stdout is None
    assert case_without_output.stderr is None


def test_junit_converter_handles_multiple_suites():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="suiteA" tests="2" failures="0" errors="0" skipped="0" time="0.01">
        <testcase classname="modA" name="case1" time="0.001" />
        <testcase classname="modA" name="case2" time="0.002" />
    </testsuite>
    <testsuite name="suiteB" tests="1" failures="1" errors="0" skipped="0" time="0.003">
        <testcase classname="modB" name="case3" time="0.003">
            <failure message="fail" />
        </testcase>
    </testsuite>
</testsuites>
"""
    junit_converter = JunitXmlConverter(xml)
    suite_runs = junit_converter.get_suite_runs()
    assert len(suite_runs) == 2
    suite_a = next(s for s in suite_runs if s.suite == "suiteA")
    suite_b = next(s for s in suite_runs if s.suite == "suiteB")
    assert suite_a.total_count == 2
    assert suite_a.fail_count == 0
    assert suite_a.status == TestSuiteRunStatus.SUCCESS
    assert suite_b.total_count == 1
    assert suite_b.fail_count == 1
    assert suite_b.status == TestSuiteRunStatus.FAILURE

    cases_a = junit_converter.get_test_cases_for_suite("suiteA")
    cases_b = junit_converter.get_test_cases_for_suite("suiteB")
    assert len(cases_a) == 2
    assert all(case.result == TestCaseRunStatus.PASS for case in cases_a)
    assert len(cases_b) == 1
    assert cases_b[0].result == TestCaseRunStatus.FAIL
    # No stdout/stderr in this XML, should be None
    for case in cases_a + cases_b:
        assert case.stdout is None
        assert case.stderr is None
