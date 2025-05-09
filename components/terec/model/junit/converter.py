"""
Convert JUnit XML format to our test result format.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

import xml.etree.ElementTree as ET

from terec.model.results import TestCaseRunStatus


class JUnitTestCase:
    """
    Represents a single test case from JUnit XML.
    """

    def __init__(
        self,
        name: str,
        classname: str,
        time: float,
        result: Optional[str] = None,
        message: Optional[str] = None,
        type: Optional[str] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ):
        """
        Initialize a JUnit test case.

        Args:
            name: Test case name
            classname: Full class name (package.class)
            time: Execution time in seconds
            result: Result type (failure, error, skipped)
            message: Error/skip message
            type: Error type
            stdout: Standard output
            stderr: Standard error
        """
        self.name = name
        self.classname = classname
        self.time = time
        self.result = result
        self.message = message
        self.type = type
        self.stdout = stdout
        self.stderr = stderr

    @property
    def test_package(self) -> str:
        """Extract package name from classname."""
        return self.classname.rsplit(".", 1)[0] if "." in self.classname else ""

    @property
    def test_suite(self) -> str:
        """Extract suite name from classname."""
        return self.classname.rsplit(".", 1)[-1]


class JUnitConverter:
    """
    Convert JUnit XML format to our test result format.
    """

    def __init__(self, xml_content: str):
        """
        Initialize the converter with XML content.

        Args:
            xml_content: JUnit XML content as string
        """
        self.root = ET.fromstring(xml_content)

    def _parse_test_case(self, element: ET.Element) -> JUnitTestCase:
        """
        Parse a single test case element.

        Args:
            element: XML element representing a test case

        Returns:
            JUnitTestCase object
        """
        # Get basic attributes
        name = element.get("name", "")
        classname = element.get("classname", "")
        time = float(element.get("time", "0"))

        # Determine result
        result = None
        message = None
        type = None

        # Check for result elements
        for child in element:
            if child.tag in ["failure", "error", "skipped"]:
                result = child.tag
                message = child.get("message", "")
                type = child.get("type", "")
                break

        # Get system output
        stdout = []
        stderr = []
        for child in element:
            if child.tag == "system-out":
                if child.text:
                    stdout.append(child.text)
            elif child.tag == "system-err":
                if child.text:
                    stderr.append(child.text)

        # Combine all system output
        stdout = "\n".join(stdout) if stdout else None
        stderr = "\n".join(stderr) if stderr else None

        return JUnitTestCase(
            name=name,
            classname=classname,
            time=time,
            result=result,
            message=message,
            type=type,
            stdout=stdout,
            stderr=stderr,
        )

    def _flatten_test_cases(self) -> List[JUnitTestCase]:
        """
        Flatten all test cases from the XML.

        Returns:
            List of JUnitTestCase objects
        """
        test_cases = []

        # Find all test cases in the XML
        for element in self.root.iter("testcase"):
            test_case = self._parse_test_case(element)
            test_cases.append(test_case)

        return test_cases

    def convert_to_json(self) -> List[Dict[str, Any]]:
        """
        Convert JUnit XML to our test result format.

        Returns:
            List of test case dictionaries in our format
        """
        test_cases = self._flatten_test_cases()

        result = []
        for test_case in test_cases:
            # Map JUnit status to our status
            if test_case.result == "skipped":
                status = TestCaseRunStatus.SKIP
            elif test_case.result in ["failure", "error"]:
                status = TestCaseRunStatus.FAIL
            else:
                status = TestCaseRunStatus.PASS

            # Convert time to milliseconds
            duration_ms = int(test_case.time * 1000)

            # Create test case info
            test_case_info = {
                "test_package": test_case.test_package,
                "test_suite": test_case.test_suite,
                "test_case": test_case.name,
                "test_config": "#",  # Default config
                "result": status.value,
                "duration_ms": duration_ms,
                "stdout": test_case.stdout,
                "stderr": test_case.stderr,
                "error_stacktrace": test_case.stderr,  # Use stderr as stacktrace
                "error_details": test_case.message,
                "skip_details": test_case.message
                if test_case.result == "skipped"
                else None,
            }

            result.append(test_case_info)

        return result
