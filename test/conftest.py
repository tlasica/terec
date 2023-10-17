import time

import pytest
from pytest_docker_fixtures import images
from pytest_docker_fixtures.containers._base import BaseImage
from tenacity import retry, wait_fixed, stop_after_attempt

#
# Configure cassandra image based on
# https://github.com/guillotinaweb/pytest-docker-fixtures
#
images.settings["cassandra"] = {}
images.configure(
    "cassandra", "cassandra", "latest", env={}, options={"ports": {"9042": "9042"}}
)


class CassandraImage(BaseImage):
    name = "cassandra"

    def check(self):
        from cassandra.cluster import ConnectionException, NoHostAvailable

        try:
            self._check_connection()
            return True
        except (ConnectionException, NoHostAvailable):
            return False

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(10))
    def _check_connection(self):
        print("trying to connect to cassandra")
        from cassandra.cluster import Cluster

        cluster = Cluster()
        cluster.connect()


cassandra_image = CassandraImage()


@pytest.fixture(scope="session")
def cassandra():
    yield cassandra_image.run()
    cassandra_image.stop()
