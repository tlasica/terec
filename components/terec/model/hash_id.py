from hashlib import sha1

from terec.model.results import TestCaseRun


def hash_id_test_case_run_d(run: TestCaseRun) -> str:
    m = sha1()
    for x in [run.org, run.project, run.suite, run.run_id]:
        m.update(bytes(str(x), 'utf-8'))
    for x in [run.test_package, run.test_suite, run.test_case, run.test_config]:
        m.update(bytes(str(x), 'utf-8'))
    return m.hexdigest()


