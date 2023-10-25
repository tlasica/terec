from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from terec.api.routers.util import get_org_or_raise
from terec.model.projects import Project
from terec.model.util import model_to_dict

router = APIRouter()


class ProjectInfo(BaseModel):
    org: str
    name: str
    full_name: str | None = None
    description: str | None = None
    url: str | None = None


@router.get("/org/{org_name}/projects")
def get_all_org_projects(org_name: str) -> list[ProjectInfo]:
    """
    Gets all projects defined for given organisation or empty list.
    If the organisation does not exist it throws exception.
    """
    get_org_or_raise(org_name)
    projects = Project.objects(org=org_name)
    res = [ProjectInfo(**model_to_dict(p)) for p in projects]
    return res


@router.post("/org/{org_name}/projects")
def create_project(org_name: str, project_info: ProjectInfo) -> ProjectInfo:
    """
    Create or update a project.
    If fields are not set then they are not updated.
    TODO: this makes it impossible to set some fields to None
    """
    get_org_or_raise(org_name)
    project_info.org = project_info.org or org_name
    assert project_info.org == org_name, "org name in body does not match the one in path"
    params = project_info.model_dump(exclude_none=True)
    return Project.create(**params)
