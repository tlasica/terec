import fastapi

from .routers import projects, results


def create_app():
    app = fastapi.FastAPI()
    app.include_router(projects.router)
    app.include_router(results.router)
    return app
