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
