
## BACKLOG

run.sh should create test/test project and org
check what is the source of branch for export-build
add test mocking jenkins server to return expected json


## 2023-12-01 Regression Detection

New regression can be based on similarity check or on the history of failures.
This will require some assumption that we collect error details or stacktrace.
We can probably stick to same test case (maybe different configs).

To implement the flow:
1. test failure is imported => event::test_case_run_failed is created
2. a worked picks up this event and analyzes it
3. if a regression is found then an event::test_case_run_regression is created
4. if notification is configured for given suite/branch then slack notification is sent (sensu?)

What we need to implement:
1. similarity check
2. test hash
3. a logic to get history and find similarities
4. an api call to find if has is a regression
5. some message queues solution
6. check what happens if events are not read





## 2023-11-22

I have used various tools to create nice tables (rich) or plots  in the cli application
inspired by this post:
https://medium.com/@SrvZ/how-to-create-stunning-graphs-in-the-terminal-with-python-2adf9d012131

And it worked well, except I was not really able to create the type of the bar plot I wanted:
with bar height being the count of failed tests. Instead I am getting always height done
proportionally from 0 to 100% of available space.

## 2023-11-18

# instead of UI build typer app and deploy in docker

1. because it is for developers
2. because it is simpler and funny exercise
3. because it will allow people to easily deploy and customize

# TODO


## Done

* PUT to add org
* GET for orgs
* adding tests should be PATCH ? No, POST is fine as we are adding/updating tests
* check if adding suite run fails on non-existing project
* export-tests should flatten tests into single list, maybe extract logic?
* can we create a k6 performance benchmark? NO: at this point we can skip it
* import performance is very low due to no asynchronous loading FIXED by unlogged batches
* generate org and project names as alphanum with - or _ FIXED by using fake.domain_name()
* check if resource name is valid when creating (org, project) FIXED by using pydantic field validators
* 

## 2023-10-18

## how to deliver the UI

idea:

## api with FastAPI

[FastAPI](https://fastapi.tiangolo.com/) looks quite promising as simple and performant framework based on conventions.
I am going to give it a try.


## cassandra in docker and cqlengine

Struggling to make things working with Cassandra in docker.
Eventually I went with `pytest-docker` plugin that  allows to start `docker-compose.yml` with fixtures.

I have also started to build database layer using `cqlengine` object-mapper for Cassandra.
It seems to work quite well so far - of course no performance tests yet.

I see some potential issues with lack of the SAI indexing, we will see if it can be solved by proper data model.

I think I will go with something quite simple with efficient and simple database plus logic in the code.

## 2023-10-16

### poetry will be used

https://python-poetry.org/docs/

```bash
sudo apt install python3-pip
sudo pip install poetry
sudo poetry self update
```

### project will be build around polylith architecture

This seems to be a valid choice for the project that will be composed
from multiple microservices or apps.

[Polylith Documentation](https://polylith.gitbook.io/polylith/)
[Python Polylith](https://davidvujic.github.io/python-polylith-docs/)

First we need to install polylith:

```bash
sudo poetry self add poetry-multiproject-plugin
sudo poetry self add poetry-polylith-plugin
```

and then we need to setup workspace

```bash
poetry poly create workspace --name terec --theme loose
```

Nice to read tutorial for the microservices polylith app with REST APIs and queues:
(https://github.com/ttamg/python-polylith-microservices-example)


## Questions

1. how to run pylint on poetry
2. how to run tests on poetry poly?
