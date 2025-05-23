import random

import faker

from conftest import random_name
from terec.model.results import TestSuite, TestSuiteRun, TestCaseRun, TestCaseRunStatus


class ResultsGenerator:
    fake = faker.Faker()

    def __init__(self, num_tests=10):
        self.tstamp = self.fake.date_time_this_month()
        self.num_tests = num_tests
        packages = ["org.example.a", "org.example.b", "org.example.c"]
        classes = ["DatabaseTests", "ModelTests", "RestTests", "LogicTests", "CliTests"]
        tests = [
            f"test_{self.fake.domain_word().replace('-', '_')}"
            for _ in range(self.num_tests)
        ]
        self.suite_runs = []
        self.test_cases = []
        for i in range(self.num_tests):
            case = {
                "test_package": random.choice(packages),
                "test_suite": random.choice(classes),
                "test_case": tests[i],
                "test_config": "#",
            }
            self.test_cases.append(case)

    def suite(self, org, project, name) -> TestSuite:
        return TestSuite.create(
            org=org,
            project=project,
            suite=name,
            url=f"http://{org}.org/{project}/{name}",
        )

    def get_suite_run(self, run_id: int):
        return next((x for x in self.suite_runs if x.run_id == run_id))

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
            "ignore": False,
        }
        s_run = TestSuiteRun.create(**params)
        self.suite_runs.append(s_run)
        return s_run

    def test_case_template(self):
        return random.choice(self.test_cases)

    def test_case_run(self, run: TestSuiteRun, case: dict, update: dict) -> TestCaseRun:
        params = case.copy()
        params["org"] = run.org
        params["project"] = run.project
        params["suite"] = run.suite
        params["branch"] = run.branch
        params["run_id"] = run.run_id
        params.update(update)
        return TestCaseRun.create(**params)

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
            case = self.test_cases[i]
            update = {"result": result.upper()}
            case_run = self.test_case_run(run, case, update)
            res.append(case_run)
        assert len(res) == run.total_count
        test_failed_count = len(
            [x for x in res if x.result == TestCaseRunStatus.FAIL.upper()]
        )
        assert (
            test_failed_count == run.fail_count
        ), f"{test_failed_count} <> expected {run.fail_count}"
        return res

    def random_output(self, n_lines: int = 1) -> str:
        return "\n".join([self.fake.sentence() for _ in range(n_lines)])

    def change_output(self, original: str, n_changes_per_line=1) -> str:
        out = []
        for line in original.splitlines(keepends=False):
            line = list(line)
            for _ in range(n_changes_per_line):
                p = random.randint(0, len(line) - 2)
                line[p], line[p + 1] = line[p + 1], line[p]
            out.append("".join(line))
        return "\n".join(out)


def generate_suite_with_test_runs(org, project, branch="main", num_runs=10):
    gen = ResultsGenerator()
    suite_name = random_name("suite")
    suite = gen.suite(org, project, suite_name)
    suite_runs = [gen.suite_run(suite, branch, n + 1) for n in range(num_runs)]
    test_runs: list[TestCaseRun] = []
    for r in suite_runs:
        test_runs += gen.test_case_runs(r)
    return suite, suite_runs, test_runs
