from __future__ import annotations

from enum import Enum

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class TestSuite(Model):
    """
    TestSuite is for example FullCI or FastCI subset of tests or CI in general, or performance tests.
    So any set of tests that is usually run on given branch and hash,
    so that we can look at the results of the tests together.
    A good example would be: Apache-Cassandra/Cassandra-4.1/CI
    """

    __test__ = False
    org = columns.Text(partition_key=True)
    project = columns.Text(primary_key=True, clustering_order="ASC")
    suite = columns.Text(primary_key=True, clustering_order="ASC")
    url = columns.Text()

    def __str__(self):
        return f"{self.org}::{self.project}::{self.suite}"


class TestSuiteRunStatus(str, Enum):
    __test__ = False
    SUCCESS = ("SUCCESS",)  # full success, all tests passed
    FAILURE = ("FAILURE",)  # some tests failed
    ERROR = "ERROR"  # some error hit, not sure if we can analyze results
    IN_PROGRESS = "IN_PROGRESS"


class TestSuiteRun(Model):
    """
    TestSuiteRun is a certain run of certain suite, for example CI build no 57 of branch B of project P.
    Example: Apache-Cassandra/Cassandra-4.1/CI/57.
    It is important for the "run_id" to be monotonic so for example build number or timestamp value
    """

    __test__ = False
    org = columns.Text(partition_key=True)
    project = columns.Text(partition_key=True)
    suite = columns.Text(partition_key=True)
    branch = columns.Text(primary_key=True, index=True)
    run_id = columns.Integer(primary_key=True, clustering_order="DESC")
    tstamp = columns.DateTime()
    commit = columns.Text()
    url = columns.Text()
    pass_count = columns.Integer()
    fail_count = columns.Integer()
    skip_count = columns.Integer()
    total_count = columns.Integer()
    duration_sec = columns.Integer()
    status = columns.Text()  # CI-provided status of the run
    ignore = columns.Boolean(
        default=False
    )  # if this suite result should be ignored by terec, even if imported
    ignore_details = columns.Text()  # why it should be ignored, user-provided

    def test_suite_str(self) -> str:
        return f"{self.org}::{self.project}::{self.suite}"

    def __str__(self):
        return f"{self.test_suite_str()}::{self.run_id}"

    def total_tests(self) -> int:
        if self.total_count is not None:
            return int(self.total_count)
        else:
            return int(self.skip_count) + int(self.fail_count) + int(self.pass_count)


class TestCaseRunStatus(str, Enum):
    __test__ = False
    PASS = ("PASS",)
    FAIL = ("FAIL",)
    SKIP = ("SKIP",)


class TestCaseRun(Model):
    @classmethod
    def create(cls, **kwargs):
        if "hash_id" not in kwargs:
            from terec.model.hash_id import hash_id_test_case_run_dict

            kwargs["hash_id"] = hash_id_test_case_run_dict(kwargs)
        return super().create(**kwargs)

    __test__ = False
    org = columns.Text(partition_key=True)
    project = columns.Text(partition_key=True)
    suite = columns.Text(partition_key=True)
    run_id = columns.Integer(partition_key=True)
    test_package = columns.Text(primary_key=True, clustering_order="ASC")
    test_suite = columns.Text(primary_key=True, clustering_order="ASC")
    test_case = columns.Text(primary_key=True, clustering_order="ASC")
    test_config = columns.Text(primary_key=True, clustering_order="ASC")
    result = columns.Text(required=True, index=True)  # PASSed, FAILed, SKIPped
    test_group = columns.Text()
    tstamp = columns.DateTime()
    duration_ms = columns.Integer()
    stdout = columns.Text()
    stderr = columns.Text()
    error_stacktrace = columns.Text()
    error_details = columns.Text()
    skip_details = columns.Text()
    hash_id = columns.Text(required=True)

    def test_suite_str(self) -> str:
        return f"{self.org}::{self.project}::{self.suite}"

    def test_case_str(self) -> str:
        case = f"{self.test_package}::{self.test_suite}::{self.test_case}"
        case += f"::{self.test_config}" if self.test_config else ""
        return f"{self.test_suite_str()}::{case}"

    def __str__(self):
        return f"{self.test_case_str()}@{self.run_id}"

    def test_case_run_id_tuple(self):
        return (
            self.test_package,
            self.test_suite,
            self.test_case,
            self.test_config,
            self.run_id,
        )

    def is_same_test_suite(self, other: TestCaseRun):
        return (
            self.test_package == other.test_package
            and self.test_suite == other.test_suite
        )

    def is_same_test_case(self, other: TestCaseRun):
        return self.test_case == other.test_case and self.is_same_test_suite(other)

    def is_same_test_case_and_config(self, other: TestCaseRun):
        return self.test_config == other.test_config and self.is_same_test_case(other)
