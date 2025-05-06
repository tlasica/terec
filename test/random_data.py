import json

from faker import Faker
from terec.api.routers.results import TestSuiteInfo, TestSuiteRunInfo, TestCaseRunInfo
from terec.model.results import TestSuiteRunStatus, TestCaseRunStatus

fake = Faker()


def random_test_suite_info(org_name: str, prj_name: str) -> TestSuiteInfo:
    ret = {
        "org": org_name,
        "project": prj_name,
        "suite": fake.word(),
        "url": fake.url(),
    }
    TestSuiteInfo.model_validate(ret)
    TestSuiteInfo.model_validate_json(json.dumps(ret))
    return TestSuiteInfo(**ret)


def random_test_suite_run_info(
    org_name: str, prj_name: str, suite_name: str, run_id: int
) -> TestSuiteRunInfo:
    pass_count = fake.random.randint(10, 100)
    skip_count = fake.random.randint(1, 10)
    fail_count = fake.random.randint(1, 10)
    run = {
        "org": org_name,
        "project": prj_name,
        "suite": suite_name,
        "run_id": run_id,
        "tstamp": str(fake.date_time_this_month()),
        "branch": "main",
        "commit": fake.md5(),
        "url": fake.url(),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "total_count": pass_count + skip_count + fail_count,
        "duration_sec": fake.random.randint(60, 120),
        "status": fake.random.choice([s for s in TestSuiteRunStatus]),
    }
    return TestSuiteRunInfo(**run)


def random_test_case_run_info(
    pkg: str = None, suite: str = None, result: str = None
) -> TestCaseRunInfo:
    run = {
        "test_package": pkg or "org.example",
        "test_suite": suite or f"Test{fake.word().capitalize()}",
        "test_case": fake.word(),
        "test_config": "#",
        "result": TestCaseRunStatus(result) if result else TestCaseRunStatus.PASS,
        "tstamp": str(fake.date_time_this_month()),
        "duration_ms": fake.random.randint(10, 10000),
    }
    return TestCaseRunInfo(**run)
