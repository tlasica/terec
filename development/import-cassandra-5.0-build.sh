set -e

export JENKINS_URL=https://ci-cassandra.apache.org/
export TEREC_ORG=apache-cassandra
export TEREC_PROJECT=cassandra

SUITE="cassandra-5.0-ci"
BUILD_NUM=$1

# collect and import suite run
poetry run cli jenkins export-build Cassandra-5.0 ${BUILD_NUM} --suite $SUITE | tee suite.json
cat suite.json | http ${TEREC_URL}/tests/orgs/${TEREC_ORG}/runs

# collect and import tests
# python run cli jenkins export-tests Cassandra-5.0 ${BUILD_NUM} > tests.json
# cat tests.json | http ${TEREC_URL}/tests/orgs/${TEREC_ORG}/projects/${TEREC_PRJ}/suites/${SUITE}/runs/${BUILD_NUM}/tests
