import copy

from terec.model.hash_id import hash_id_test_case_run
from terec.model.results import TestCaseRun


def test_should_return_same_hash_for_same_test_case_run_data():
    run_1 = TestCaseRun()
    run_1.org = "some_org"
    run_1.project = "some_project"
    run_1.suite = "some_suite"
    run_1.test_package = "org.example"
    run_1.test_suite = "SomeTest"
    run_1.test_case = "some_test_case"
    run_1.test_config = "#"
    run_2 = copy.deepcopy(run_1)
    hash_id_1 = hash_id_test_case_run(run_1)
    hash_id_2 = hash_id_test_case_run(run_2)
    assert hash_id_1 is not None
    assert len(hash_id_1) == 40
    assert hash_id_1 == hash_id_2


def test_should_return_different_hash_for_different_test_case_run_config():
    run_1 = TestCaseRun()
    run_1.org = "some_org"
    run_1.project = "some_project"
    run_1.suite = "some_suite"
    run_1.test_package = "org.example"
    run_1.test_suite = "SomeTest"
    run_1.test_case = "some_test_case"
    run_1.test_config = "#"
    run_2 = copy.deepcopy(run_1)
    run_2.test_config = "###"
    hash_id_1 = hash_id_test_case_run(run_1)
    hash_id_2 = hash_id_test_case_run(run_2)
    assert hash_id_1 != hash_id_2
