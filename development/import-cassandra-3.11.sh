set -e

export JENKINS_URL=https://ci-cassandra.apache.org/
export TEREC_ORG=apache
export TEREC_PRJ=cassandra

SUITE="cassandra-3.11-ci"
BUILD_NUM=$1

# collect and import suite run
python bases/terec/jenkins_cli/main.py pipeline export-build Cassandra-3.11 ${BUILD_NUM} --suite ${SUITE} | tee suite.json
cat suite.json | http localhost:8000/tests/orgs/${TEREC_ORG}/runs

# collect and import tests
python bases/terec/jenkins_cli/main.py pipeline export-tests Cassandra-3.11 ${BUILD_NUM} > tests.json
cat tests.json | http localhost:8000/tests/orgs/${TEREC_ORG}/projects/${TEREC_PRJ}/suites/${SUITE}/runs/${BUILD_NUM}/tests

