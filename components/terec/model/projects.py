from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

# TODO: shall we try the model based on names or rather use uuids?
# TODO: it may be a good idea to allow some metadata for projects as a text->text map


class Org(Model):
    """
    Organization such as e.g. ApacheCassandra or DSE or any opensource project.
    Organization can have multiple Projects e.g:
    - for Cassandra a project may be Cassandra-3.1, Cassandra-4.0 or Cassandra-5.0
    - for some company projects may be AppX, ServiceY etc.
    """

    name = columns.Text(primary_key=True)
    full_name = columns.Text()
    url = columns.Text()


class Project(Model):
    """
    A project that can have one or many Suites of tests executed to measure/judge quality.
    For example a project can have a FullCI suite and a FastCI suite with limited set of tests.
    It can also have a PerformanceTests or maybe DeploymentTests.
    """

    org_name = columns.Text(primary_key=True)
    prj_name = columns.Text(primary_key=True, clustering_order="ASC")
    full_name = columns.Text()
    description = columns.Text()
    url = columns.Text()
