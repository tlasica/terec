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
    org_name = columns.Text(partition_key=True)
    prj_name = columns.Text(primary_key=True, clustering_order="ASC")
    suite_name = columns.Text(primary_key=True, clustering_order="ASC")
    url = columns.Text()

    def __str__(self):
        return f"{self.org_id}::{self.prj_id}::{self.suite_name}"


class TestSuiteRun(Model):
    """
    TestSuiteRun is a certain run of certain suite, for example CI build no 57 of branch B of project P.
    Example: Apache-Cassandra/Cassandra-4.1/CI/57.
    It is important for the "run_id" to be monotonic so for example build number or timestamp value
    """

    __test__ = False
    org_name = columns.Text(partition_key=True)
    prj_name = columns.Text(partition_key=True)
    suite_name = columns.Text(partition_key=True)
    run_id = columns.Integer(primary_key=True, clustering_order="DESC")
    tstamp = columns.DateTime()
    branch = columns.Text()
    commit = columns.Text()
    url = columns.Text()
    passed_tests = columns.Integer()
    failed_tests = columns.Integer()
    skipped_tests = columns.Integer()
    duration_sec = columns.Integer()

    def test_suite_str(self) -> str:
        return f"{self.org_id}::{self.prj_id}::{self.suite_name}"

    def __str__(self):
        return f"{self.test_suite_str()}::{self.run_id}"


class TestCaseRun(Model):
    __test__ = False
    org_name = columns.Text(partition_key=True)
    prj_name = columns.Text(partition_key=True)
    suite_name = columns.Text(partition_key=True)
    run_id = columns.Integer(partition_key=True)
    package = columns.Text(primary_key=True, clustering_order="ASC")
    suite = columns.Text(primary_key=True, clustering_order="ASC")
    test_case = columns.Text(primary_key=True, clustering_order="ASC")
    test_config = columns.Text(primary_key=True, clustering_order="ASC")
    result = columns.Text(required=True)
    tstamp = columns.DateTime()
    duration_sec = columns.Integer()
    std_out = columns.Text()
    std_err = columns.Text()
    stack_trace = columns.Text()

    def test_suite_str(self) -> str:
        return f""

    def test_case_str(self) -> str:
        return f""

    def __str__(self):
        return ""
