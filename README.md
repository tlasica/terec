# TeReC - the Test Result Collector

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Key functions

1. Collect results from multiple builds/test runs in one place
2. Allow/Block PR merging based on the test results even with flickering tests
~~3. Automatically detect test regression early and inform project members~~
~~4. Support developers with creating tickets (jira, gh issues) for failed tests~~

## User Guide

See [USERGUIDE](./USER_GUIDE.md)

## Architecture

This software is inspired by the [butler]() tool co-created by me while working for [Datastax]()
and is aiming at more modular and modern architecture:

1. Separate logic from the UI
2. Use microservices and message queues to decompose the logic and allow scalability
3. Use Apache Cassandra compatible database for keeping the data
4. Organize project using the [Polylith](https://polylith.gitbook.io/polylith) architecture

## Tech Stack

1. implemented in [Python]
2. with FastAPI for REST API calls
3. with [RabbitMQ]() for events
4. using [Docker]() for deployments

## Development

### Project structure

Project is organized using [polylith](https://polylith.gitbook.io/polylith) concept.

### Build and tasks

Build is done with [poetry] and [poe]

To see all tasks (defined in [pyproject.toml](./pyproject.toml)) run `poe`.
Most important task to run will be `poe build` and `poe test`.

### Testing

Running tests (including simple benchmarks) is described in [TESTING.md](./TESTING.md)

## Docs
* The official Polylith documentation: [high-level documentation](https://polylith.gitbook.io/polylith)
* A Python implementation of the Polylith tool: [python-polylith](https://github.com/DavidVujic/python-polylith)
