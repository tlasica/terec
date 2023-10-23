from faker import Faker
from terec.model.projects import Org, Project

fake = Faker()


def test_create_org(cassandra_model):
    org = Org.create(
        name=fake.company(), full_name="My Organisation", url="https://my.org/"
    )
    assert org is not None


def test_find_org_by_name(cassandra_model):
    # given an org created among multiple others
    org_name = fake.company()
    Org.create(name=org_name, full_name="My Org", url="https://my.org/")
    for i in range(0, 10):
        Org.create(name=fake.company())
    assert Org.objects().count() >= 11
    # when org is searched
    search = Org.objects(name=org_name)
    assert search.count() == 1
    found = search[0]
    # then it is found with proper full name and description
    assert found.name == org_name
    assert found.full_name == "My Org"
    assert found.url == "https://my.org/"


def test_create_projects_in_org(cassandra_model):
    # given an org with multiple projects
    org_name = fake.company()
    prj_name = fake.domain_word()
    Org.create(name=org_name, full_name="My Org", url="https://my.org/")
    Project.create(org_name=org_name, prj_name=prj_name, full_name="My Project")
    for i in range(0, 10):
        Project.create(org_name=org_name, prj_name=fake.company())
    # when projects in org are searched then it has all inserted
    projects = Project.objects(org_name=org_name)
    assert projects.count() == 11
    # when certain project is searched by name then it is found
    my_project = Project.objects(org_name=org_name, prj_name=prj_name)
    assert my_project.count() == 1
    my_project = my_project[0]
    assert my_project.full_name == "My Project"
