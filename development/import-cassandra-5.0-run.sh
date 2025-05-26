set -e

export JENKINS_URL=https://ci-cassandra.apache.org/
export TEREC_ORG=apache-cassandra
export TEREC_PROJECT=cassandra

SUITE="cassandra-5.0-ci"
BUILD_NUM=$1

# collect and import suite run
poetry run cli jenkins import-run Cassandra-5.0 ${BUILD_NUM} $SUITE
