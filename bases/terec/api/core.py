import fastapi

from .routers import failures, plots, projects, results


def create_app():
    app = fastapi.FastAPI()
    app.include_router(projects.router, prefix="/admin")
    app.include_router(results.router, prefix="/tests")
    app.include_router(plots.router, prefix="/history")
    app.include_router(failures.router, prefix="/history")
    return app
