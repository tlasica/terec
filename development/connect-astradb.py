from terec.database import cassandra_session
from terec.model.util import cqlengine_init

# initialize cassandra connection
cassandra = cassandra_session()
cqlengine_init(cassandra)
