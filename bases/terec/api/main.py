import fastapi

from .routers import projects
from terec.database import cassandra_session
from terec.model.util import cqlengine_init


app = fastapi.FastAPI()
app.include_router(projects.router)

cassandra = cassandra_session()
cqlengine_init(cassandra)
