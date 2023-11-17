import json
import os
import typer
from fastapi.encoders import jsonable_encoder

from terec.ci_jenkins.jenkins_server import JenkinsServer


pipeline_app = typer.Typer()


def jenkins_server() -> JenkinsServer:
    url = os.environ.get("JENKINS_URL", None)
    if not url:
        raise ValueError("JENKINS_URL is not set or empty.")
    return JenkinsServer(url)


def value_or_env(val: str, env_var: str) -> str:
    return val or os.environ.get(env_var, None)


@pipeline_app.command()
def export_build(
    job: str, build: int, org: str = None, project: str = None, suite: str = None
):
    """
    Collect build information from the Jenkins-CI job described by provided url.
    Output is the terec-importable json for the test suite run info.
    Requires JENKINS_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: what about branch and suite, we probably need to pass them as parameters as well
    """
    server = jenkins_server()
    info = server.suite_run_for_build(job_name=job, build_num=build)
    info.org = value_or_env(org, "TEREC_ORG") or info.org
    info.project = value_or_env(project, "TEREC_PRJ") or info.project
    info.suite = suite if suite else info.suite
    data = jsonable_encoder(info, exclude_none=True)
    json_data = json.dumps(data, indent=2)
    print(json_data)


@pipeline_app.command()
def export_tests(job: str, build: int):
    server = jenkins_server()
    print("[")
    first_suite = True
    for suite in server.suite_test_runs_for_build(job_name=job, build_num=build):
        if not first_suite:
            print(",")
        first_suite = False
        data = jsonable_encoder(suite, exclude_none=True)
        json_data = json.dumps(data, indent=2)
        print(json_data)
    print("]")
