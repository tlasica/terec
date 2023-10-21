import fastapi

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from pydantic import BaseModel
from typing import Optional

from terec.database import cassandra_session
from terec.model import structure, model_to_dict

# TODO: move it to external file like main or core and use routing
app = fastapi.FastAPI()

# TODO: do we need to run sync? on table Org?
cassandra = cassandra_session()
connection.set_session(cassandra)
sync_table(structure.Org)
sync_table(structure.Project)


class ProjectInfo(BaseModel):
    org_name: str
    prj_name: str
    full_name: str | None = None
    description: str | None = None
    url: str | None = None


@app.get("/org/{org_name}/projects")
def get_all_org_projects(org_name: str) -> list[ProjectInfo]:
    """
    Gets all projects defined for given organisation or empty list.
    If the organization does not exist it throws exception [TODO]
    """
    projects = structure.Project.objects(org_name=org_name)
    res = [ProjectInfo(**model_to_dict(p)) for p in projects]
    return res
