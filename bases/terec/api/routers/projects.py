from fastapi import APIRouter
from pydantic import BaseModel

from terec.model.projects import Project
from terec.model.util import model_to_dict

router = APIRouter()


# TODO: probably we should move it from router to model package
class ProjectInfo(BaseModel):
    org_name: str
    prj_name: str
    full_name: str | None = None
    description: str | None = None
    url: str | None = None


@router.get("/org/{org_name}/projects")
def get_all_org_projects(org_name: str) -> list[ProjectInfo]:
    """
    Gets all projects defined for given organisation or empty list.
    If the organization does not exist it throws exception [TODO]
    """
    projects = Project.objects(org_name=org_name)
    res = [ProjectInfo(**model_to_dict(p)) for p in projects]
    return res
