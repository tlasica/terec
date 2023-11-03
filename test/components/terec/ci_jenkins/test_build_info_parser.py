from terec.model.results import TestSuiteRunStatus
from .sample_data.build_info import sample_build_info
from terec.ci_jenkins.build_info_parser import build_info_to_suite_run


def test_build_info_parser() -> None:
    parsed = build_info_to_suite_run(
        "Apache", "Cassandra", "Cassandra-3.11", sample_build_info()
    )
    assert parsed.status == TestSuiteRunStatus.FAILURE
    assert parsed.pass_count == 17357
