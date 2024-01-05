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

