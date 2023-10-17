"""
Keep connection parameters in the env variables
as this will make it easy to pass to docker or use in testing.
TODO: shall we support connecting to Astra DB (requires secure bundle)
TODO: maybe we will have to add some case class CassandraConfig and pass it
"""

import os

from cassandra.cluster import Cluster, Session
from cassandra.auth import DSEPlainTextAuthProvider

CASSANDRA_HOSTS = os.getenv('CASSANDRA_HOSTS', None)
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT', None)
CASSANDRA_USER = os.getenv('CASSANDRA_USER', None)
CASSANDRA_PASSWORD = os.getenv('CASSANDRA_PASS', None)


def cassandra_cluster() -> Cluster:
    options = {}
    if CASSANDRA_HOSTS:
        options["contact_points"] = CASSANDRA_HOSTS.split(",")
    if CASSANDRA_PORT:
        options["port"] = int(CASSANDRA_PORT)
    if CASSANDRA_USER:
        assert CASSANDRA_PORT, "When CASSANDRA_USER is set it is required to set CASSANDRA_PORT as well."
        auth_provider = DSEPlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PASSWORD)
        options["auth_provider"] = auth_provider
    # return Cluster(**options)
    return Cluster(**options)


def cassandra_session() -> Session:
    """
    Return connection to the database
    """
    return cassandra_cluster().connect()
