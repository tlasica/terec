### Running tests

`poetry run pytest` should be enough to run full test suite.

`poetry run pytest --keepalive` will run the tests and keep docker compose up.

### Troubleshooting

1. If port 9042 is used stop docker `docker kill pytest-terec-cassandra-1` or run `docker ps` and kill test containers.
2. In case of the `cqlengine` sync failure run `cqlsh` and `DROP KEYSPACE terec` to cleanup schema.

### Integration Tests

Integration tests required docker containers for example for the database.
The approach is based on https://pypi.org/project/pytest-docker/
with `docker-compose.yaml` file.

A per-session fixture `cassandra` is available for tests that require database connection.

I have also considered/checked: 
* https://pypi.org/project/pytest-docker-fixtures/
* https://xnuinside.medium.com/integration-testing-for-bunch-of-services-with-pytest-docker-compose-4892668f9cba
* https://github.com/pytest-docker-compose/pytest-docker-compose

