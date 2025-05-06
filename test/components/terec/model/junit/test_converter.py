"""
Tests for JUnit XML converter.
"""

import pytest
from datetime import datetime
import xml.etree.ElementTree as ET

from terec.model.results import TestCaseRunStatus
from terec.model.junit.converter import JUnitConverter, JUnitTestCase


def test_parse_test_case_with_multiple_system_output():
    """
    Test parsing a test case with multiple system output elements.
    """
    xml_content = """
    <testcase name="testDebug" classname="com.example.debug.DebugTest" time="0.1">
        <system-out><![CDATA[Debug output line 1]]></system-out>
        <system-out><![CDATA[Debug output line 2]]></system-out>
        <system-err><![CDATA[Error output line 1]]></system-err>
        <system-err><![CDATA[Error output line 2]]></system-err>
        <system-err><![CDATA[Error output line 3]]></system-err>
    </testcase>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testDebug"
    assert test_case.classname == "com.example.debug.DebugTest"
    assert test_case.time == 0.1
    assert test_case.result is None
    assert test_case.stdout == "Debug output line 1\nDebug output line 2"
    assert (
        test_case.stderr
        == "Error output line 1\nError output line 2\nError output line 3"
    )


def test_parse_test_case_with_no_time():
    """
    Test parsing a test case with no time attribute (should default to 0).
    """
    xml_content = """
    <testcase name="testNoTime" classname="com.example.no.time.Test"/>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testNoTime"
    assert test_case.classname == "com.example.no.time.Test"
    assert test_case.time == 0.0
    assert test_case.result is None


def test_parse_test_case_with_no_classname():
    """
    Test parsing a test case with no classname (should handle gracefully).
    """
    xml_content = """
    <testcase name="testNoClassname"/>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testNoClassname"
    assert test_case.classname == ""
    assert test_case.time == 0.0
    assert test_case.result is None


def test_parse_test_case_with_assertions():
    """
    Test parsing a test case with assertions attribute.
    """
    xml_content = """
    <testcase name="testAssert" classname="com.example.assert.Test" time="0.5" assertions="3">
    </testcase>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testAssert"
    assert test_case.classname == "com.example.assert.Test"
    assert test_case.time == 0.5
    assert test_case.result is None


def test_parse_test_case_with_failure():
    """
    Test parsing a test case with failure element.
    """
    xml_content = """
    <testcase name="testFail" classname="com.example.fail.Test" time="0.2">
        <failure type="java.lang.AssertionError" message="Expected value to be 5">
            <![CDATA[
            org.opentest4j.AssertionFailedError: Expected value to be 5
                at org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:55)
            ]]>
        </failure>
    </testcase>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testFail"
    assert test_case.classname == "com.example.fail.Test"
    assert test_case.time == 0.2
    assert test_case.result == "failure"
    assert test_case.message == "Expected value to be 5"
    assert test_case.type == "java.lang.AssertionError"


def test_parse_test_case_with_error():
    """
    Test parsing a test case with error element.
    """
    xml_content = """
    <testcase name="testError" classname="com.example.error.Test" time="0.3">
        <error type="java.lang.RuntimeException" message="Something went wrong">
            <![CDATA[
            java.lang.RuntimeException: Something went wrong
                at com.example.error.Test.testError(Test.java:10)
            ]]>
        </error>
    </testcase>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testError"
    assert test_case.classname == "com.example.error.Test"
    assert test_case.time == 0.3
    assert test_case.result == "error"
    assert test_case.message == "Something went wrong"
    assert test_case.type == "java.lang.RuntimeException"


def test_parse_test_case_with_skip():
    """
    Test parsing a test case with skip element.
    """
    xml_content = """
    <testcase name="testSkip" classname="com.example.skip.Test" time="0.0">
        <skipped type="org.junit.jupiter.api.extension.TestAbortedException" message="Test skipped due to condition">
            <![CDATA[
            Test skipped due to condition
            ]]>
        </skipped>
    </testcase>
    """

    converter = JUnitConverter(xml_content)
    test_case = converter._parse_test_case(ET.fromstring(xml_content))

    assert test_case.name == "testSkip"
    assert test_case.classname == "com.example.skip.Test"
    assert test_case.time == 0.0
    assert test_case.result == "skipped"
    assert test_case.message == "Test skipped due to condition"
    assert test_case.type == "org.junit.jupiter.api.extension.TestAbortedException"
