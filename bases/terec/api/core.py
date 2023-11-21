import fastapi

from .routers import plots, projects, results


def create_app():
    app = fastapi.FastAPI()
    app.include_router(projects.router)
    app.include_router(results.router)
    app.include_router(plots.router)
    return app
