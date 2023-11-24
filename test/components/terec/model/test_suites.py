import pytest
from faker import Faker

from terec.model.results import TestSuite

fake = Faker()


def test_get_test_suites_for_project(cassandra_model, test_project):
    suite_names = ["fast-ci", "full-ci"]
    for name in suite_names:
        TestSuite.create(
            org=test_project.org,
            project=test_project.name,
            suite=name,
        )
    suites = TestSuite.objects(org=test_project.org, project=test_project.name)
    assert len(suites) >= 2
    names = {s.suite for s in suites}
    assert suites[0].suite in names
    assert suites[1].suite in names


def test_get_test_suites_for_org(cassandra_model, test_project):
    suite_names = ["fast-ci", "full-ci"]
    for name in suite_names:
        TestSuite.create(
            org=test_project.org,
            project=test_project.name,
            suite=name,
        )
    suites = TestSuite.objects(org=test_project.org)
    assert len(suites) >= 2
    names = {s.suite for s in suites}
    assert suites[0].suite in names
    assert suites[1].suite in names


def test_create_test_suite_without_name_should_fail(cassandra_model, test_project):
    from cassandra import InvalidRequest

    with pytest.raises(InvalidRequest):
        TestSuite.create(
            org=test_project.org,
            project=test_project.name,
            suite=None,
        )


def test_create_test_suite_twice_should_override(cassandra_model, test_project):
    org_name = fake.company()
    prj_name = fake.company()
    suite_name = fake.vin()
    for i in range(2):
        TestSuite.create(
            org=org_name,
            project=prj_name,
            suite=suite_name,
        )
    suites = TestSuite.objects(org=org_name)
    assert len(suites) == 1
    assert suites[0].suite == suite_name
