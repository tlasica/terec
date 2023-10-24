from fastapi import HTTPException

from terec.model.projects import Org


def get_org_or_raise(org_name: str) -> Org:
    assert org_name
    org = Org.objects(name=org_name)
    if not org:
        raise HTTPException(
            status_code=404, detail=f"Org {org_name} not found in the database."
        )
    return org
