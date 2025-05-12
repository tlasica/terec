# Operating TeReC

Before starting `TeReC` it needs to be built:
```commandline
poe build
```

To start local deployment (single C* node) run:
```bash
docker compose -f ./deploy/local/docker-compose.yaml up -d
```
and to stop:
```bash
docker compose -f ./deploy/local/docker-compose.yaml down
```

# Importing data

Importing data is currently supported:
1. from terec-compatible json files via api endpoints
2. from junix xml files
3. from jenkins runs

## Importing from json files

To import data from json files it is required to make two api calls:
- to import suite runs
- to import test results for this run

Please take a look at the [examples](./doc/EXAMPLE.md) or to exposed swagger / openapi docs.

## Import from junit xml file

Following command will import both suite run info and test results
from the `pytest-report.xml` file.

Data will be imported for org `terec` and project `terec`
for branch `main` and run number 2.

```bash
poetry run python bases/terec/import_cli/main.py junit convert \
./pytest-report.xml main 2 \
--org terec --project terec
```

Note: suite name is taken from top level `testsuite` junit xml node.

## Import from jenkins server

Importing from jenkins server is done in two steps:
1. export data from jenkins in the terec-compatible json format
2. import (1) using api endpoints (mentioned earlier in this section)

Please take a look at following command to export the data:
```bash
poetry run python bases/terec/jenkins_cli/main.py --help
```

# Accessing data

Accessing data is through terec `cli` commands.

## builds history

```bash
python bases/terec/status_cli/main.py builds history \
cassandra-3.11-ci origin/cassandra-3.11
```

![output](doc/builds-history.png)

## builds show

```bash
python bases/terec/status_cli/main.py builds show \
cassandra-3.11-ci 512
```

![output](doc/builds-show.png)

## tests history

```bash
python bases/terec/status_cli/main.py tests history \
cassandra-3.11-ci origin/cassandra-3.11 --threshold 10
```

![output](doc/tests-history.png)


## tests failed

```bash
python bases/terec/status_cli/main.py tests failed \
cassandra-3.11-ci origin/cassandra-3.11 --limit 12 --threshold 10
```

![output](doc/tests-failed.png)


## tests regression-check

```bash
python bases/terec/status_cli/main.py tests regression-check \
cassandra-3.11-ci --run-id 510
```

![output](doc/tests-regression-check.png)
