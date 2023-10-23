import os

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from terec.model import projects, results


def cqlengine_init(cassandra):
    """
    Initializes cql engine and syncs all tables.
    """
    if os.getenv("CQLENG_ALLOW_SCHEMA_MANAGEMENT") is None:
        os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "1"
    connection.set_session(cassandra)
    sync_table(projects.Org)
    sync_table(projects.Project)
    sync_table(results.TestSuite)
    sync_table(results.TestSuiteRun)
    sync_table(results.TestCaseRun)


def model_to_dict(model_instance):
    """
    Used to translate cqlengine.Model to dictionary
    so that it can be later translated to other models e.g. pydantic BaseModel
    TODO: how to map between cqlengine.Model and pydantic.BaseModel in an elegant way
    """
    result = {}
    for field_name, field in model_instance._columns.items():
        result[field_name] = getattr(model_instance, field_name)
    return result
