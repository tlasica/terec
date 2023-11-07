import datetime

from terec.api.routers.results import TestSuiteRunInfo
from terec.model.results import TestSuiteRunStatus


WORKFLOW_RUN_CLASS = "org.jenkinsci.plugins.workflow.job.WorkflowRun"

# TODO: maybe we need a ci_status: Text without translation? and is_valid + use_build??

BUILD_RESULT_TO_STATUS = {
    "UNSTABLE": TestSuiteRunStatus.FAILURE,
    "SUCCESS": TestSuiteRunStatus.SUCCESS,
    "FAILURE": TestSuiteRunStatus.ERROR,
    "ABORTED": TestSuiteRunStatus.ERROR,
    "CANCELED": TestSuiteRunStatus.ERROR,
    "BUILDING": TestSuiteRunStatus.IN_PROGRESS,
}


def build_status(result: str) -> TestSuiteRunStatus:
    ci_status = result.upper()
    assert ci_status in BUILD_RESULT_TO_STATUS
    return BUILD_RESULT_TO_STATUS[ci_status]


def parse_jenkins_build_info(
    org: str, project: str, suite: str, build: dict
) -> TestSuiteRunInfo:
    assert (
        build["_class"] == WORKFLOW_RUN_CLASS
    ), f"Build class {build['_class']} is not supported: only {WORKFLOW_RUN_CLASS} is supported."

    run = {
        "org": org,
        "project": project,
        "suite": suite,
        "run_id": int(build["number"]),
        "tstamp": datetime.datetime.fromtimestamp(build["timestamp"] // 1000),
        "url": build["url"],
        "duration_sec": int(build["duration"]) // 1000,
        "status": build_status(build["result"]),
    }

    extras = {x["_class"]: x for x in build["actions"] if x and "_class" in x}

    if "hudson.tasks.junit.TestResultAction" in extras:
        results = extras["hudson.tasks.junit.TestResultAction"]
        run["fail_count"] = int(results["failCount"])
        run["skip_count"] = int(results["skipCount"])
        run["total_count"] = int(results["totalCount"])
        run["pass_count"] = run["total_count"] - run["skip_count"] - run["fail_count"]

    if "hudson.plugins.git.util.BuildData" in extras:
        branch_info = extras["hudson.plugins.git.util.BuildData"]["lastBuiltRevision"][
            "branch"
        ][0]
        run["branch"] = branch_info["name"]
        run["commit"] = branch_info["SHA1"]

    return TestSuiteRunInfo(**run)
