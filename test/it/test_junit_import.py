"""
End-to-end test for JUnit XML import.
"""

import json
import os

from faker import Faker
from pytest import fixture
from starlette.testclient import TestClient

from assertions import raise_for_status
from random_data import random_test_suite_run_info
from terec.api.core import create_app
from terec.model.junit.converter import JUnitConverter
from terec_api_client import TerecApiClient


class TestJUnitConverterImport:

    api_app = create_app()
    api_client = TestClient(api_app)
    terec_api = TerecApiClient(api_client)
    fake = Faker()

    @fixture(scope="class")
    def org_and_project(self) -> tuple[str, str]:
        org_name = self.fake.domain_name()
        self.terec_api.put_org(name=org_name)
        self.terec_api.put_project(org_name=org_name, name="prj")
        return org_name, "prj"

    def test_import_junit_basic(self, cassandra_model, examples_dir, org_and_project):
        org, prj = org_and_project
        junit_xml_file = os.path.join(examples_dir, "junit/junit-basic.xml")
        self._test_import_junit(junit_xml_file, org, prj, "basic")

    def test_import_junit_complete(
        self, cassandra_model, examples_dir, org_and_project
    ):
        org, prj = org_and_project
        junit_xml_file = os.path.join(examples_dir, "junit/junit-complete.xml")
        self._test_import_junit(junit_xml_file, org, prj, "complete")

    def test_import_pytest(self, cassandra_model, examples_dir, org_and_project):
        org, prj = org_and_project
        junit_xml_file = os.path.join(examples_dir, "junit/pytest-report.xml")
        self._test_import_junit(junit_xml_file, org, prj, "pytest")

    def _test_import_junit(self, xml_path: str, org: str, prj: str, suite: str):
        junit_xml = self._read_file(xml_path)

        converter = JUnitConverter(junit_xml)
        test_results_json = json.dumps(converter.convert_to_json(), indent=2)

        self.terec_api.post_suite(org, prj, suite)
        suite_run = random_test_suite_run_info(org, prj, suite, 1)
        self.terec_api.post_suite_run(org, suite_run)

        resp = self.terec_api.post_test_results(
            org, prj, suite, "main", 1, test_results_json
        )
        raise_for_status(resp)

    def _read_file(self, file_path: str):
        with open(file_path, "rt") as f:
            return "\n".join(f.readlines())
