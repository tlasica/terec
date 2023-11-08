import jenkins

# connect to jenkins server
j = jenkins.Jenkins("https://ci-cassandra.apache.org/")

# get build test result report
test_result = j.get_build_test_report("Cassandra-3.11", 503)

test_result.keys()
# this result is in suites but it also has some summary information
# Out[8]: dict_keys(['_class', 'testActions', 'duration', 'empty', 'failCount', 'passCount', 'skipCount', 'suites'])

suites = test_result["suites"]
len(suites)
