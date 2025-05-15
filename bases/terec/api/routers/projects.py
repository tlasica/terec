from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel, field_validator

from terec.api.auth import req_admin_perm
from terec.api.routers.util import (
    get_org_or_raise,
    raise_if_org_exists,
    is_valid_terec_name,
)
from terec.model.projects import Project, Org, generate_org_tokens, OrgToken
from terec.model.util import model_to_dict

router = APIRouter()


class OrgInfo(BaseModel):
    name: str
    full_name: str | None = None
    url: str | None = None
    private: bool = False

    @classmethod
    @field_validator("name", mode="plain")
    def name_must_be_valid(cls, v: str) -> str:
        if not is_valid_terec_name(v):
            raise ValueError(
                "Org name should start and end with alnum and contain only {alnum,.,_,-}."
            )
        return v


class OrgTokenInfo(BaseModel):
    token_name: str
    token: str


class ProjectInfo(BaseModel):
    org: str
    name: str
    full_name: str | None = None
    description: str | None = None
    url: str | None = None

    @classmethod
    @field_validator("name", "org", mode="plain")
    def name_must_be_valid(cls, v: str) -> str:
        if not is_valid_terec_name(v):
            raise ValueError(
                "Org name should start and end with alphanum and contain only {alphanum,.,_,-}."
            )
        return v


@router.get("/orgs")
def get_all_orgs() -> list[OrgInfo]:
    orgs = Org.objects()
    res = [OrgInfo(**model_to_dict(o)) for o in orgs]
    return res


@router.put("/orgs", status_code=201)
def create_org(org_info: OrgInfo) -> dict:
    raise_if_org_exists(org_info.name)
    params = org_info.model_dump(exclude_none=True)
    org = Org.create(**params)
    org_tokens = {}
    if org.private:
        logger.info("Generating tokens for private org: {}", org.name)
        for token, token_data in generate_org_tokens(org.name):
            OrgToken.create(**model_to_dict(token_data))
            org_tokens[token_data.token_name] = token
        return {
            "message": f"Private org {org.name} created. Please store tokens in a safe place.",
            "tokens": org_tokens,
        }
    else:
        return {
            "message": f"Public org {org.name} created. Tokens not required.",
            "tokens": [],
        }


@router.get("/orgs/{org_name}/projects")
def get_all_org_projects(org_name: str) -> list[ProjectInfo]:
    """
    Gets all projects defined for given organisation or empty list.
    If the organisation does not exist it throws exception.
    """
    get_org_or_raise(org_name)
    projects = Project.objects(org=org_name)
    res = [ProjectInfo(**model_to_dict(p)) for p in projects]
    return res


@router.put("/orgs/{org_name}/projects", status_code=201)
def create_project(
    org_name: str,
    project_info: ProjectInfo,
    authz: str = Depends(req_admin_perm),
) -> ProjectInfo:
    """
    Create or update a project.
    If fields are not set then they are not updated.
    TODO: this makes it impossible to set some fields to None
    """
    get_org_or_raise(org_name)
    project_info.org = project_info.org or org_name
    assert (
        project_info.org == org_name
    ), "org name in body does not match the one in path"
    params = project_info.model_dump(exclude_none=True)
    return Project.create(**params)
