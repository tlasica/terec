from functools import lru_cache

from fastapi import HTTPException, status, Path, Depends
from fastapi.security import APIKeyHeader
from loguru import logger

from terec.model.projects import Org, OrgToken
from terec.auth.tokens import verify_token

header_scheme = APIKeyHeader(
    name="X-API-KEY",
    scheme_name="API Key",
    description="API Key required for private organisations, generated on org create.",
    auto_error=False,
)


# TODO: later add permission: admin, read, write
def validate_org_token(
    org_name: str = Path(..., description="Organization identifier in the path"),
    api_key: str | None = Depends(header_scheme),
):
    """
    Validates the token if the organization requires it.
    If the organization is private, an HTTP 401 exception is raised for an invalid or missing token.
    """
    if not _is_org_private(org_name):
        logger.debug("Org {} is not private. skip token validation", org_name)
        return

    if not api_key:
        _raise_unauthorized("Token required for private organization")

    org_token = _check_token(org_name, api_key)
    if not org_token:
        _raise_unauthorized("Invalid token")

    return org_token.token_name or org_token.token_id


@lru_cache(maxsize=1024)
def _is_org_private(org_name: str) -> bool:
    org = Org.objects(name=org_name).first()
    return org.private if org else False


@lru_cache(maxsize=1024)
def _check_token(org_name: str, token: str) -> OrgToken | None:
    org_tokens = OrgToken.objects(org=org_name)
    for t in org_tokens:
        if verify_token(token, t.token_hash.encode("utf-8")):
            return t
    return None


def _raise_unauthorized(detail: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": 'ApiKey realm="Access to the protected API"'},
    )
