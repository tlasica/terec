import typer
from terec.status_cli.builds_commands import builds_app
from terec.status_cli.tests_commands import tests_app

app = typer.Typer()
app.add_typer(builds_app, name="builds")
app.add_typer(tests_app, name="tests")

if __name__ == "__main__":
    app()
