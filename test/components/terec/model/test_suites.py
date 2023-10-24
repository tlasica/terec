import pytest
from faker import Faker

from terec.model.results import TestSuite

fake = Faker()


def test_get_test_suites_for_project(cassandra_model, test_project):
    suite_names = ["fast-ci", "full-ci"]
    for name in suite_names:
        TestSuite.create(
            org_name=test_project.org_name,
            prj_name=test_project.prj_name,
            suite_name=name,
        )
    suites = TestSuite.objects(
        org_name=test_project.org_name, prj_name=test_project.prj_name
    )
    assert len(suites) == 2
    assert suites[0].suite_name == suite_names[0]
    assert suites[1].suite_name == suite_names[1]


def test_get_test_suites_for_org(cassandra_model, test_project):
    suite_names = ["fast-ci", "full-ci"]
    for name in suite_names:
        TestSuite.create(
            org_name=test_project.org_name,
            prj_name=test_project.prj_name,
            suite_name=name,
        )
    suites = TestSuite.objects(org_name=test_project.org_name)
    assert len(suites) == 2
    assert suites[0].suite_name == suite_names[0]
    assert suites[1].suite_name == suite_names[1]


def test_create_test_suite_without_name_should_fail(cassandra_model, test_project):
    from cassandra import InvalidRequest

    with pytest.raises(InvalidRequest):
        TestSuite.create(
            org_name=test_project.org_name,
            prj_name=test_project.prj_name,
            suite_name=None,
        )


def test_create_test_suite_twice_should_override(cassandra_model, test_project):
    org_name = fake.company()
    prj_name = fake.company()
    suite_name = fake.vin()
    for i in range(2):
        TestSuite.create(
            org_name=org_name,
            prj_name=prj_name,
            suite_name=suite_name,
        )
    suites = TestSuite.objects(org_name=org_name)
    assert len(suites) == 1
    assert suites[0].suite_name == suite_name
