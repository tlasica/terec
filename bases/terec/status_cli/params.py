import typer


OPT_ORG = typer.Option(
    None, help="org id, if not used then TEREC_ORG env var will be used"
)

OPT_PRJ = typer.Option(
    None, help="project id, if not used then TEREC_PRJ env var will be used"
)

OPT_FOLD = typer.Option(
    False, help="if set test case will be presented in single column"
)

OPT_BUILDS_LIMIT = typer.Option(16, help="number of past builds to use")

ARG_SUITE = typer.Argument(help="which suite runs to plot")

ARG_BRANCH = typer.Argument(help="branch to select suite runs")

ARG_RUN_ID = typer.Argument(help="suite (build) run id")

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

OPT_PROGRESS = typer.Option(False, help="show progress in stderr")
