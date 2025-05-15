import uuid

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from datetime import datetime, timezone

from terec.auth.tokens import generate_token, hash_token


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
    private = columns.Boolean(default=False)


class Project(Model):
    """
    A project that can have one or many Suites of tests executed to measure/judge quality.
    For example a project can have a FullCI suite and a FastCI suite with limited set of tests.
    It can also have a PerformanceTests or maybe DeploymentTests.
    """

    org = columns.Text(primary_key=True)
    name = columns.Text(primary_key=True, clustering_order="ASC")
    full_name = columns.Text()
    description = columns.Text()
    url = columns.Text()


class OrgToken(Model):
    """
    Token assigned for the organization during creation.
    For each token we do keep a hash of it so that we can check if it is valid.
    Tokens are given permissions: READ, WRITE, ADMIN
    """

    PERM_READ = "READ"
    PERM_WRITE = "WRITE"
    PERM_ADMIN = "ADMIN"

    org = columns.Text(primary_key=True)
    token_id = columns.UUID(primary_key=True, clustering_order="ASC")
    token_hash = columns.Text()
    token_name = columns.Text()
    created_at = columns.DateTime(default=datetime.now(timezone.utc))
    expire_at = columns.DateTime()
    permissions = columns.Set(columns.Text)

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions


def generate_org_tokens(org_name: str) -> list[tuple[str, OrgToken]]:
    tokens = [
        _org_token(
            org_name,
            "admin",
            [OrgToken.PERM_READ, OrgToken.PERM_WRITE, OrgToken.PERM_ADMIN],
        ),
        _org_token(org_name, "write", [OrgToken.PERM_READ, OrgToken.PERM_WRITE]),
        _org_token(org_name, "read", [OrgToken.PERM_READ]),
    ]
    return tokens


def _org_token(
    org_name: str, name: str, permissions: list[str]
) -> tuple[str, OrgToken]:
    token = generate_token()
    org_token = OrgToken(
        org=org_name,
        token_id=uuid.uuid4(),
        token_hash=hash_token(token).decode("utf-8"),
        token_name=name,
        permissions=permissions,
    )
    return token, org_token
