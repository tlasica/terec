set -e

export JENKINS_URL=https://ci-cassandra.apache.org/
export TEREC_ORG=apache-cassandra
export TEREC_PROJECT=cassandra

SUITE="cassandra-5.0-ci"
BUILD_NUM=$1

FILE="tests-${BUILD_NUM}.json"

# collect and import tests
if [ ! -f "$FILE" ] || [ ! -s "$FILE" ]; then
    poetry run cli jenkins export-tests Cassandra-5.0 ${BUILD_NUM} > "$FILE"
fi
cat "${FILE}" | http --json --compress ${TEREC_URL}/tests/orgs/${TEREC_ORG}/projects/${TEREC_PROJECT}/suites/${SUITE}/branches/${origin--cassandra-5.0}/runs/${BUILD_NUM}/tests
# rm "$FILE"
