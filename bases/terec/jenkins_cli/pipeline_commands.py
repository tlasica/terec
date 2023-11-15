import json
import os
import typer
from fastapi.encoders import jsonable_encoder

from terec.ci_jenkins.jenkins_server import JenkinsServer


JENKINS_URL = os.environ.get("JENKINS_URL", None)

TEREC_ORG = os.environ.get("TEREC_ORG", None)
TEREC_PROJECT = os.environ.get("TEREC_PROJECT", None)

pipeline_app = typer.Typer()


@pipeline_app.command()
def export_build(job: str, build: int, org: str = TEREC_ORG, project: str = TEREC_PROJECT, suite: str = None):
    """
    Collect build information from the Jenkins-CI job described by provided url.
    Output is the terec-importable json for the test suite run info.
    Requires JENKINS_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: what about branch and suite, we probably need to pass them as parameters as well
    """
    if not JENKINS_URL:
        raise ValueError("JENKINS_URL is not set or empty.")
    server = JenkinsServer(JENKINS_URL)
    info = server.suite_run_for_build(job_name=job, build_num=build)
    info.org = org if org else info.org
    info.project = project if project else info.project
    info.suite = suite if suite else info.suite
    data = jsonable_encoder(info, exclude_none=True)
    json_data = json.dumps(data, indent=2)
    print(json_data)


@pipeline_app.command()
def export_tests(job: str, build: int):
    if not JENKINS_URL:
        raise ValueError("JENKINS_URL is not set or empty.")
    server = JenkinsServer(JENKINS_URL)
    print("[")
    for suite in server.suite_test_runs_for_build(job_name=job, build_num=build):
        data = jsonable_encoder(suite, exclude_none=True)
        json_data = json.dumps(data, indent=2)
        print(json_data)
    print("]")
