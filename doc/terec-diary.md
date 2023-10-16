##  2023-10-16

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


