import datetime

from terec.api.routers.results import TestCaseRunInfo
from terec.model.results import TestCaseRunStatus


def parse_report_suite(suite: dict) -> list[TestCaseRunInfo]:
    """
    Translates jenkins test result suite into list of TestCaseRunInfo objects.
    Note: config is set to provided after "-" or to # if not provided.
    Subsequent occurrences of the same test case name (unfortunately it is possible)
    are created with #, ## and so on configurations.
    TODO: it is possible that [case-config] existing multiple types will be an issue...
    """
    ret = []
    names = {}
    tstamp = datetime.datetime.fromisoformat(suite["timestamp"])
    for case in suite["cases"]:
        test_package, test_suite = split_fq_class_name(case["className"])
        test_name, test_config = split_case_name_with_config(case["name"])
        if not test_config:
            test_config = "#" * (1 + names.get(test_name, 0))
        case_info = {
            "test_package": test_package or "#",
            "test_suite": test_suite,
            "test_case": test_name,
            "test_config": test_config,
            "result": case_run_status(case["status"]),
            "test_group": None,     # should be decided later
            "tstamp": tstamp,
            "duration_ms": float(case["duration"]) * 1000 if "duration" in case else None,
            "stdout": case.get("stdout", None),
            "stderr": case.get("stderr", None),
            "error_stacktrace": case.get("errorStackTrace", None),
            "error_details": case.get("errorDetails", None),
            "skip_details": case.get("skippedMessage", None)
        }
        ret.append(TestCaseRunInfo(**case_info))
        names[test_name] = 1 + names.get(test_name, 0)

    return ret


def split_fq_class_name(fq_class_name: str) -> tuple[str | None, str]:
    """
    Split class name into package (potentially None) and suite (class) names.
    """
    if "." in fq_class_name:
        i = fq_class_name.rfind(".")
        return fq_class_name[:i], fq_class_name[i+1:]
    else:
        return None, fq_class_name


def split_case_name_with_config(name: str) -> tuple[str, str | None]:
    """
    Split test case name into case name and config using - as delimiter.
    This is some arbitrary convention as jenkins does not support such thing as "configuration".
    """
    if "-" in name:
        i = name.find("-")
        return name[:i], name[i+1:]
    else:
        return name, None


def case_run_status(status: str) -> TestCaseRunStatus:
    if status in ["PASSED", "FIXED"]:
        return TestCaseRunStatus.PASS
    elif status in ["FAILED", "REGRESSION"]:
        return TestCaseRunStatus.FAIL
    elif status in ["SKIPPED"]:
        return TestCaseRunStatus.SKIP
    else:
        assert False, f"Unknown test case status: {status}"

