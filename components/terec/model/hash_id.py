from hashlib import sha1

from terec.model.results import TestCaseRun


def hash_id_test_case_run(run: TestCaseRun) -> str:
    data = [run.org, run.project, run.suite, str(run.run_id)]
    data += [run.test_package, run.test_suite, run.test_case, run.test_config]
    return _hash_id(data)


def hash_id_test_case_run_dict(run: dict) -> str:
    data = []
    for k in ["org", "project", "suite", "run_id"]:
        data.append(str(run[k]))
    for k in ["test_package", "test_suite", "test_case", "test_config"]:
        data.append(str(run[k]))
    return _hash_id(data)


def _hash_id(data: list[str]) -> str:
    m = sha1()
    for s in data:
        m.update(bytes(s, 'utf-8'))
    return m.hexdigest()
