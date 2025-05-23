import json
import os
import typer
from more_itertools import flatten

from terec.lib.terec_api_client import TerecApiClient
from terec.util import cli_params

jenkins_app = typer.Typer()


def jenkins_server():
    from terec.ci_jenkins.jenkins_server import JenkinsServer

    url = os.environ.get("JENKINS_URL", None)
    if not url:
        raise ValueError("JENKINS_URL is not set or empty.")
    return JenkinsServer(url)


def value_or_env(val: str, env_var: str) -> str:
    return val or os.environ.get(env_var, None)


@jenkins_app.command()
def export_build(
    job: str, build: int, org: str = None, project: str = None, suite: str = None
):
    """
    Collect build information from the Jenkins-CI job described by provided url.
    Output is the terec-importable json for the test suite run info.
    Requires JENKINS_URL to be set and optionally TEREC_ORG, TEREC_PROJECT.

    TODO: what about branch and suite, we probably need to pass them as parameters as well
    """
    from fastapi.encoders import jsonable_encoder

    server = jenkins_server()
    info = server.suite_run_for_build(job_name=job, build_num=build)
    info.org = value_or_env(org, "TEREC_ORG") or info.org
    info.project = value_or_env(project, "TEREC_PROJECT") or info.project
    info.suite = suite if suite else info.suite
    data = jsonable_encoder(info, exclude_none=True)
    json_data = json.dumps(data, indent=2)
    print(json_data)


@jenkins_app.command()
def import_run(
    job: str,
    build: int,
    org: str = cli_params.OPT_ORG,
    project: str = cli_params.OPT_PRJ,
    suite: str = cli_params.ARG_SUITE,
):
    """
    Import test data for a specific Jenkins build into the system.
    """
    from fastapi.encoders import jsonable_encoder

    # download build info
    typer.echo("Connecting to jenkins server")
    server = jenkins_server()

    typer.echo(f"Getting build from jenkins server {server.url}")
    info = server.suite_run_for_build(job_name=job, build_num=build)
    info.org = value_or_env(org, "TEREC_ORG") or info.org
    info.project = value_or_env(project, "TEREC_PROJECT") or info.project
    info.suite = suite if suite else info.suite

    # import build info into terec
    api_client = TerecApiClient()
    typer.echo(f"Importing build info to terec at {api_client.terec_url}")
    import_build_path = f"/tests/orgs/{org}/runs"
    data = jsonable_encoder(info, exclude_none=True)
    api_client.post(path=import_build_path, body=data)
    typer.echo("Suite run info imported")

    # now import test results in batches
    branch = info.branch
    limit = 0
    typer.echo(f"Importing test results in batches. Branch: {branch}")
    import_tests_path = f"/tests/orgs/{org}/projects/{project}/suites/{suite}/branches/{branch}/runs/{build}/tests"
    for batch in server.suite_test_runs_for_build(
        job_name=job, build_num=build, limit=limit
    ):
        typer.echo(f"Importing batch..")
        data = jsonable_encoder(list(flatten(batch)), exclude_none=True)
        resp = api_client.post(path=import_tests_path, body=data)
        typer.echo(f"Imported {resp}")


@jenkins_app.command()
def export_tests(
    job: str,
    build: int,
    limit: int = typer.Option(0, help="limit for number of suites exported"),
) -> int:
    from fastapi.encoders import jsonable_encoder

    exported_cnt = 0
    server = jenkins_server()
    print("[")
    for suite in server.suite_test_runs_for_build(
        job_name=job, build_num=build, limit=limit
    ):
        data = jsonable_encoder(suite, exclude_none=True)
        for item in data:
            if exported_cnt > 0:
                print(",")
            print(json.dumps(item, indent=2))
            exported_cnt += 1
    print("]")
    return exported_cnt
