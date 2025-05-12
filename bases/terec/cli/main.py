import typer
from terec.cli.builds_commands import builds_app
from terec.cli.tests_commands import tests_app
from terec.cli.junit_commands import junit_app
from terec.cli.jenkins_commands import jenkins_app

# Create the main Typer app
app = typer.Typer()

# Add existing command groups
app.add_typer(builds_app, name="builds")
app.add_typer(tests_app, name="tests")
app.add_typer(junit_app, name="junit")
app.add_typer(jenkins_app, name="jenkins")

# Entry point
if __name__ == "__main__":
    app()
