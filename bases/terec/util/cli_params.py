import typer


OPT_API_KEY = typer.Option(
    default=None,
    envvar="TEREC_API_KEY",
    help="X-API-KEY token required for private orgs.",
)

OPT_ORG = typer.Option(
    None,
    envvar="TEREC_ORG",
    help="org id, if not used then TEREC_ORG env var will be used",
)

OPT_PRJ = typer.Option(
    None,
    envvar="TEREC_PROJECT",
    help="project id, if not used then TEREC_PROJECT env var will be used",
)

OPT_FOLD: bool = typer.Option(
    False, help="if set test case will be presented in single column"
)

OPT_BUILDS_LIMIT: int = typer.Option(16, help="number of past builds to use")

ARG_SUITE: str = typer.Argument(help="which suite runs to plot")

ARG_BRANCH: str = typer.Argument(help="branch to select suite runs")

ARG_RUN_ID: int = typer.Argument(help="suite (build) run id")

BUILD_FIELDS = [
    "fail_count",
    "skip_count",
    "pass_count",
    "total_count",
    "duration_sec",
]

ARG_BUILD_FIELD = (
    typer.Option("fail_count", help=f"field to use from {BUILD_FIELDS}"),
)

OPT_PROGRESS: bool = typer.Option(False, help="show progress in stderr")
