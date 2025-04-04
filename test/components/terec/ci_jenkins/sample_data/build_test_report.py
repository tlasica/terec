def sample_build_test_report_suite() -> dict:
    return {
        "cases": [
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 65.771,
                "errorDetails": None,
                "errorStackTrace": None,
                "failedSince": 0,
                "name": "multiColumn",
                "skipped": False,
                "skippedMessage": None,
                "status": "PASSED",
                "stderr": "",
                "stdout": "INFO  [main] <main> 2023-10-26 14:01:50,525 Versions.java:136 - Looking for dtest jars in /home/cassandra/cassandra/build\nFound 3.0.30\nFound 2.2.20\nFound 4.0.12\nFound 4.1.4\nFound 3.11.17\ntesting upgrade from 2.2.20 to 3.0.30\nINFO  [main] <main> 2023-10-26 14:01:52,684 Reflections.java:219 - Reflections took 1790 ms to scan 6 urls, producing 1031 keys and 5790 values\nNode id topology:\nnode 1: dc = datacenter0, rack = rack0\nnode 2: dc = datacenter0, rack = rack0\nnode 3: dc = datacenter0, rack = ra\n...[truncated 2269618 chars]...\nInitializing index summary manager with a memory pool size of 50 MB and a resize interval of 60 minutes\nINFO  [node1_isolatedExecutor:6] node1 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node2_isolatedExecutor:6] node2 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node3_isolatedExecutor:6] node3 2023-10-26 14:02:55,578 MessagingService.java:985 - Waiting for messaging service to quiesce\n",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 65.815,
                "errorDetails": None,
                "errorStackTrace": None,
                "failedSince": 0,
                "name": "multiColumn",
                "skipped": False,
                "skippedMessage": None,
                "status": "PASSED",
                "stderr": "",
                "stdout": "INFO  [main] <main> 2023-10-26 14:01:50,525 Versions.java:136 - Looking for dtest jars in /home/cassandra/cassandra/build\nFound 3.0.30\nFound 2.2.20\nFound 4.0.12\nFound 4.1.4\nFound 3.11.17\ntesting upgrade from 2.2.20 to 3.0.30\nINFO  [main] <main> 2023-10-26 14:01:52,684 Reflections.java:219 - Reflections took 1790 ms to scan 6 urls, producing 1031 keys and 5790 values\nNode id topology:\nnode 1: dc = datacenter0, rack = rack0\nnode 2: dc = datacenter0, rack = rack0\nnode 3: dc = datacenter0, rack = ra\n...[truncated 2269618 chars]...\nInitializing index summary manager with a memory pool size of 50 MB and a resize interval of 60 minutes\nINFO  [node1_isolatedExecutor:6] node1 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node2_isolatedExecutor:6] node2 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node3_isolatedExecutor:6] node3 2023-10-26 14:02:55,578 MessagingService.java:985 - Waiting for messaging service to quiesce\n",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 60.453,
                "errorDetails": None,
                "errorStackTrace": None,
                "failedSince": 0,
                "name": "multiColumn",
                "skipped": False,
                "skippedMessage": None,
                "status": "PASSED",
                "stderr": "",
                "stdout": "INFO  [main] <main> 2023-10-26 14:01:50,525 Versions.java:136 - Looking for dtest jars in /home/cassandra/cassandra/build\nFound 3.0.30\nFound 2.2.20\nFound 4.0.12\nFound 4.1.4\nFound 3.11.17\ntesting upgrade from 2.2.20 to 3.0.30\nINFO  [main] <main> 2023-10-26 14:01:52,684 Reflections.java:219 - Reflections took 1790 ms to scan 6 urls, producing 1031 keys and 5790 values\nNode id topology:\nnode 1: dc = datacenter0, rack = rack0\nnode 2: dc = datacenter0, rack = rack0\nnode 3: dc = datacenter0, rack = ra\n...[truncated 2269618 chars]...\nInitializing index summary manager with a memory pool size of 50 MB and a resize interval of 60 minutes\nINFO  [node1_isolatedExecutor:6] node1 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node2_isolatedExecutor:6] node2 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node3_isolatedExecutor:6] node3 2023-10-26 14:02:55,578 MessagingService.java:985 - Waiting for messaging service to quiesce\n",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 60.453,
                "errorDetails": None,
                "errorStackTrace": None,
                "failedSince": 0,
                "name": "skipped_test",
                "skipped": True,
                "skippedMessage": "not applicable",
                "status": "SKIPPED",
                "stderr": "",
                "stdout": "INFO  [main] <main> 2023-10-26 14:01:50,525 Versions.java:136 - Looking for dtest jars in /home/cassandra/cassandra/build\nFound 3.0.30\nFound 2.2.20\nFound 4.0.12\nFound 4.1.4\nFound 3.11.17\ntesting upgrade from 2.2.20 to 3.0.30\nINFO  [main] <main> 2023-10-26 14:01:52,684 Reflections.java:219 - Reflections took 1790 ms to scan 6 urls, producing 1031 keys and 5790 values\nNode id topology:\nnode 1: dc = datacenter0, rack = rack0\nnode 2: dc = datacenter0, rack = rack0\nnode 3: dc = datacenter0, rack = ra\n...[truncated 2269618 chars]...\nInitializing index summary manager with a memory pool size of 50 MB and a resize interval of 60 minutes\nINFO  [node1_isolatedExecutor:6] node1 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node2_isolatedExecutor:6] node2 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node3_isolatedExecutor:6] node3 2023-10-26 14:02:55,578 MessagingService.java:985 - Waiting for messaging service to quiesce\n",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 60.453,
                "errorDetails": "error details example",
                "errorStackTrace": "stack trace example",
                "failedSince": 0,
                "name": "failed_test",
                "skipped": True,
                "skippedMessage": "not applicable",
                "status": "FAILED",
                "stderr": "stderr example",
                "stdout": "stdout example",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "duration": 60.453,
                "errorDetails": "error details example",
                "errorStackTrace": "stack trace example",
                "failedSince": 0,
                "name": "regression_test",
                "skipped": True,
                "skippedMessage": "not applicable",
                "status": "REGRESSION",
                "stderr": "stderr example",
                "stdout": "stdout example",
            },
            {
                "testActions": [
                    {"_class": "de.esailors.jenkins.teststability.StabilityTestAction"}
                ],
                "age": 0,
                "className": "org.example.SomeTest",
                "name": "skinny_test",
                "skipped": True,
                "status": "PASSED",
            },
        ],
        "duration": 192.448,
        "enclosingBlockNames": ["Summary"],
        "enclosingBlocks": ["367"],
        "id": None,
        "name": "org.example.SomeTest",
        "nodeId": "371",
        "stderr": "",
        "stdout": "INFO  [main] <main> 2023-10-26 14:01:50,525 Versions.java:136 - Looking for dtest jars in /home/cassandra/cassandra/build\nFound 3.0.30\nFound 2.2.20\nFound 4.0.12\nFound 4.1.4\nFound 3.11.17\ntesting upgrade from 2.2.20 to 3.0.30\nINFO  [main] <main> 2023-10-26 14:01:52,684 Reflections.java:219 - Reflections took 1790 ms to scan 6 urls, producing 1031 keys and 5790 values\nNode id topology:\nnode 1: dc = datacenter0, rack = rack0\nnode 2: dc = datacenter0, rack = rack0\nnode 3: dc = datacenter0, rack = ra\n...[truncated 2269618 chars]...\nInitializing index summary manager with a memory pool size of 50 MB and a resize interval of 60 minutes\nINFO  [node1_isolatedExecutor:6] node1 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node2_isolatedExecutor:6] node2 2023-10-26 14:02:55,571 MessagingService.java:985 - Waiting for messaging service to quiesce\nINFO  [node3_isolatedExecutor:6] node3 2023-10-26 14:02:55,578 MessagingService.java:985 - Waiting for messaging service to quiesce\n",
        "timestamp": "2023-10-26T14:01:50",
    }
