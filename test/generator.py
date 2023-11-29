import random

import faker

from terec.model.results import TestSuite, TestSuiteRun, TestCaseRun, TestCaseRunStatus


class ResultsGenerator:

    fake = faker.Faker()

    def __init__(self, num_tests=10):
        self.tstamp = self.fake.date_time_this_month()
        self.num_tests = num_tests
        packages = ["org.example.a", "org.example.b", "org.example.c"]
        classes = ["DatabaseTests", "ModelTests", "RestTests", "LogicTests", "CliTests"]
        tests = [f"test_{self.fake.domain_word().replace('-', '_')}" for _ in range(self.num_tests)]
        self.test_cases = []
        for i in range(self.num_tests):
            case = {
                "test_package": random.choice(packages),
                "test_suite": random.choice(classes),
                "test_case": tests[i],
                "test_config": "#"
            }
            self.test_cases.append(case)

    def suite(self, org, project, name) -> TestSuite:
        return TestSuite.create(org=org, project=project, suite=name, url=f"http://{org}.org/{project}/{name}")

    def suite_run(self, suite: TestSuite, branch: str, run_id: int) -> TestSuiteRun:
        skip_count = random.randint(0, self.num_tests // 5)
        fail_count = random.randint(0, self.num_tests // 10)
        pass_count = self.num_tests - skip_count - fail_count
        params = {
            "org": suite.org,
            "project": suite.project,
            "suite": suite.suite,
            "branch": branch,
            "run_id": run_id,
            "tstamp": self.tstamp,
            "url": f"{suite.url}/{run_id}" if suite.url else None,
            "pass_count": pass_count,
            "skip_count": skip_count,
            "fail_count": fail_count,
            "total_count": self.num_tests,
            "duration_sec": random.randint(30, 120),
            "status": "SUCCESS" if fail_count == 0 else "FAILURE",
            "ignore": False
        }
        return TestSuiteRun.create(**params)

    def test_case_runs(self, run: TestSuiteRun) -> list[TestCaseRun]:
        """
        Generate proper number of test cases based on run information with following guarantees:
        - FAIL and SKIP tests will meet run.fail_count and run.skip_count;
        - total number of rows generated will match total_count
        """
        res = []
        for i in range(run.total_count):
            result = TestCaseRunStatus.PASS
            if i < run.fail_count:
                result = TestCaseRunStatus.FAIL
            elif i < run.fail_count + run.skip_count:
                result = TestCaseRunStatus.SKIP
            params = self.test_cases[i].copy()
            params["org"] = run.org
            params["project"] = run.project
            params["suite"] = run.suite
            params["run_id"] = run.run_id
            params["result"] = result.upper()
            case_run = TestCaseRun.create(**params)
            res.append(case_run)
        assert len(res) == run.total_count
        test_failed_count = len([x for x in res if x.result == TestCaseRunStatus.FAIL.upper()])
        assert test_failed_count == run.fail_count, f"{test_failed_count} <> expected {run.fail_count}"
        return res
