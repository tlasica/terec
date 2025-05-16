import typer

from terec.cli.admin_cli import admin_app
from terec.cli.builds_commands import builds_app
from terec.cli.tests_commands import tests_app
from terec.cli.junit_commands import junit_app
from terec.cli.jenkins_commands import jenkins_app

# Create the main Typer app
app = typer.Typer()

# Add existing command groups
app.add_typer(admin_app, name="admin")
app.add_typer(
    builds_app, name="builds", short_help="Commands on builds (suite runs) history."
)
app.add_typer(tests_app, name="tests", short_help="Commands on test cases history.")
app.add_typer(junit_app, name="junit")
app.add_typer(
    jenkins_app, name="jenkins", short_help="Export Jenkins CI builds and test reports."
)


@app.command(short_help="Prints common env variables to be set when using cli.")
def env():
    typer.echo("Common env variables:")
    typer.echo("TEREC_URL - for the TeReC api url.")
    typer.echo("TEREC_API_KEY - api key for private orgs.")
    typer.echo("TEREC_ORG - org name (instead of --org)")
    typer.echo("TEREC_PROJECT - project name (instead of --project)")


# Entry point
if __name__ == "__main__":
    app()
