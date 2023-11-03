def sample_build_info() -> dict:
    return {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowRun",
        "actions": [
            {
                "_class": "hudson.model.CauseAction",
                "causes": [
                    {
                        "_class": "hudson.model.Cause$UserIdCause",
                        "shortDescription": "Started by user Stefan Miklosovic",
                        "userId": "smiklosovic",
                        "userName": "Stefan Miklosovic",
                    }
                ],
            },
            {},
            {},
            {
                "_class": "jenkins.metrics.impl.TimeInQueueAction",
                "blockedDurationMillis": 0,
                "blockedTimeMillis": 0,
                "buildableDurationMillis": 0,
                "buildableTimeMillis": 0,
                "buildingDurationMillis": 29729334,
                "executingTimeMillis": 29729334,
                "executorUtilization": 1.0,
                "subTaskCount": 0,
                "waitingDurationMillis": 1,
                "waitingTimeMillis": 1,
            },
            {},
            {
                "_class": "hudson.plugins.git.util.BuildData",
                "buildsByBranchName": {
                    "origin/cassandra-3.11": {
                        "_class": "hudson.plugins.git.util.Build",
                        "buildNumber": 501,
                        "buildResult": None,
                        "marked": {
                            "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                            "branch": [
                                {
                                    "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                                    "name": "origin/cassandra-3.11",
                                }
                            ],
                        },
                        "revision": {
                            "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                            "branch": [
                                {
                                    "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                                    "name": "origin/cassandra-3.11",
                                }
                            ],
                        },
                    }
                },
                "lastBuiltRevision": {
                    "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                    "branch": [
                        {
                            "SHA1": "6212b0aaa524b004c4a2477b4e5383b08ebc354b",
                            "name": "origin/cassandra-3.11",
                        }
                    ],
                },
                "remoteUrls": ["https://github.com/apache/cassandra.git"],
                "scmName": "",
            },
            {},
            {"_class": "org.jenkinsci.plugins.workflow.libs.LibrariesAction"},
            {},
            {"_class": "org.jenkinsci.plugins.workflow.cps.EnvActionImpl"},
            {},
            {},
            {
                "_class": "hudson.tasks.junit.TestResultAction",
                "failCount": 12,
                "skipCount": 1650,
                "totalCount": 19019,
                "urlName": "testReport",
            },
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {"_class": "org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction"},
            {
                "_class": "org.jenkinsci.plugins.pipeline.modeldefinition.actions.RestartDeclarativePipelineAction"
            },
            {},
            {"_class": "org.jenkinsci.plugins.workflow.job.views.FlowGraphAction"},
            {},
            {},
            {},
            {},
        ],
        "artifacts": [],
        "building": False,
        "description": None,
        "displayName": "#501",
        "duration": 29729334,
        "estimatedDuration": 30820435,
        "executor": None,
        "fullDisplayName": "Cassandra-3.11 #501",
        "id": "501",
        "keepLog": False,
        "number": 501,
        "queueId": 274867,
        "result": "UNSTABLE",
        "timestamp": 1697722383329,
        "url": "https://ci-cassandra.apache.org/job/Cassandra-3.11/501/",
        "changeSets": [],
        "culprits": [
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/brandonwilliams",
                "fullName": "Brandon Williams",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/edimitrova",
                "fullName": "Ekaterina Dimitrova",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/smiklosovic",
                "fullName": "Stefan Miklosovic",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/jonmeredith",
                "fullName": "Jon Meredith",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/jlewandowski",
                "fullName": "Jacek Lewandowski",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/mck",
                "fullName": "Michael Semb Wever",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/a.penya.garcia",
                "fullName": "a.penya.garcia",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/ifesdjeen",
                "fullName": "Alex Petrov",
            },
            {
                "absoluteUrl": "https://ci-cassandra.apache.org/user/branimir.lambov",
                "fullName": "branimir.lambov",
            },
        ],
        "nextBuild": {
            "number": 502,
            "url": "https://ci-cassandra.apache.org/job/Cassandra-3.11/502/",
        },
        "previousBuild": {
            "number": 500,
            "url": "https://ci-cassandra.apache.org/job/Cassandra-3.11/500/",
        },
    }
