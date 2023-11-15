import typer
from terec.jenkins_cli.pipeline_commands import pipeline_app

app = typer.Typer()
app.add_typer(pipeline_app, name="pipeline")

if __name__ == "__main__":
    app()
