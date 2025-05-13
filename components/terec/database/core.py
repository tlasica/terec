"""
Keep connection parameters in the env variables
as this will make it easy to pass to docker or use in testing.
TODO: maybe we will have to add some case class CassandraConfig and pass it
"""

import os

from cassandra.cluster import (
    Cluster,
    Session,
    ExecutionProfile,
    EXEC_PROFILE_DEFAULT,
    ProtocolVersion,
)
from cassandra.auth import DSEPlainTextAuthProvider, PlainTextAuthProvider
from loguru import logger


CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", None)
CASSANDRA_PORT = os.getenv("CASSANDRA_PORT", None)
CASSANDRA_USER = os.getenv("CASSANDRA_USER", None)
CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASS", None)
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "terec")


ASTRADB_SCB_PATH = os.getenv("ASTRADB_SCB_PATH", None)
ASTRADB_TOKEN = os.getenv("ASTRADB_TOKEN", None)


def cassandra_session(drop_keyspace: bool = False) -> Session:
    """
    Return connection to the database with keyspace created if not exists
    TODO: keyspace management should be moved outside
    """
    if _is_astradb():
        logger.info("Connecting to Astra DB using {}", ASTRADB_SCB_PATH)
        session = _astradb_cluster().connect()
    else:
        logger.info("Connecting to Cassandra using {}", CASSANDRA_HOSTS)
        session = _cassandra_cluster().connect()
        _prepare_keyspace(session, drop_keyspace)

    logger.info("Connected using keyspace {}", CASSANDRA_KEYSPACE)
    session.set_keyspace(CASSANDRA_KEYSPACE)
    return session


def _is_astradb():
    return ASTRADB_SCB_PATH is not None and ASTRADB_SCB_PATH != ""


def _cassandra_cluster() -> Cluster:
    options = {"protocol_version": 5}
    if CASSANDRA_HOSTS:
        options["contact_points"] = CASSANDRA_HOSTS.split(",")
    if CASSANDRA_PORT:
        options["port"] = int(CASSANDRA_PORT)
    if CASSANDRA_USER:
        assert (
            CASSANDRA_PORT
        ), "When CASSANDRA_USER is set it is required to set CASSANDRA_PORT as well."
        auth_provider = DSEPlainTextAuthProvider(
            username=CASSANDRA_USER, password=CASSANDRA_PASSWORD
        )
        options["auth_provider"] = auth_provider
    return Cluster(**options)


def _astradb_cluster() -> Cluster:
    """
    Makes connection to Astra DB.
    https://docs.datastax.com/en/astra-db-serverless/databases/python-driver.html
    """
    assert ASTRADB_SCB_PATH, "ASTRADB_SCB_PATH is not set"
    assert ASTRADB_TOKEN, "ASTRADB_TOKEN is not set"
    cloud_config = {"secure_connect_bundle": ASTRADB_SCB_PATH, "connect_timeout": 30}
    auth_provider = PlainTextAuthProvider("token", ASTRADB_TOKEN)
    profile = ExecutionProfile(request_timeout=30)
    return Cluster(
        cloud=cloud_config,
        auth_provider=auth_provider,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
        protocol_version=ProtocolVersion.V4,
    )


def _prepare_keyspace(session, drop_keyspace: bool = False) -> None:
    if drop_keyspace:
        session.execute(f"DROP KEYSPACE IF EXISTS {CASSANDRA_KEYSPACE};")

    replication_strategy = {
        "class": "SimpleStrategy",
        "replication_factor": 1,  # Adjust replication factor as needed
    }
    query = f"CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} WITH replication = {str(replication_strategy)}"
    session.execute(query)
