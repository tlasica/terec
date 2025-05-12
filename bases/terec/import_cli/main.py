import typer
from terec.import_cli.junit_commands import junit_app

app = typer.Typer()
app.add_typer(junit_app, name="junit")

if __name__ == "__main__":
    app()
