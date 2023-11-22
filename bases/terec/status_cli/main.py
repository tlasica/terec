import typer
from terec.status_cli.builds_commands import builds_app

app = typer.Typer()
app.add_typer(builds_app, name="builds")

if __name__ == "__main__":
    app()
