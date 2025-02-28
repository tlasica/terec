# TeReC - the Test Result Collector

## Key functions

1. Collect results from multiple builds/test runs in one place
2. Allow/Block PR merging based on the test results even with flickering tests
3. Automatically detect test regression early and inform project members
4. Support developers with creating tickets (jira, gh issues) for failed tests  

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

## Docs
* The official Polylith documentation: [high-level documentation](https://polylith.gitbook.io/polylith)
* A Python implementation of the Polylith tool: [python-polylith](https://github.com/DavidVujic/python-polylith)
