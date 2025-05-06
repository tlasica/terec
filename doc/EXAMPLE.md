# API Examples

## Creating a New Organization

To create a new organization, use the following curl command:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X PUT "http://localhost:8000/admin/orgs" \
  -H "Content-Type: application/json" \
  -d '{"name": "your-org-name", "full_name": "Your Organization Name", "url": "http://your-org.example.com"}'
```

Replace `your-org-name`, `Your Organization Name`, and `http://your-org.example.com` with your desired values.

The command will:
- `-v`: Enable verbose output to see the request/response details
- `-w "\nResponse code: %{response_code}\n"`: Show the HTTP response code
- `-X PUT`: Use PUT method for creating/updating the organization
- `-H "Content-Type: application/json"`: Set the content type to JSON
- `-d`: Send the organization data as JSON

Expected responses:
- `201 Created`: Organization was successfully created
- `403 Forbidden`: Organization already exists

## Listing All Organizations

To list all organizations, use:

```bash
curl -X GET "http://localhost:8000/admin/orgs"
```

This will return a JSON array of all organizations in the system.

## Creating a New Project

To create a new project within an organization, use:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X PUT "http://localhost:8000/admin/orgs/myorg123/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "myproject123", "full_name": "My Project", "description": "First project in organization", "url": "http://myproject123.example.com", "org": "myorg123"}'
```

Replace `myorg123` and `myproject123` with your desired values.

The command will:
- `-v`: Enable verbose output to see the request/response details
- `-w "\nResponse code: %{response_code}\n"`: Show the HTTP response code
- `-X PUT`: Use PUT method for creating/updating the project
- `-H "Content-Type: application/json"`: Set the content type to JSON
- `-d`: Send the project data as JSON

Expected responses:
- `201 Created`: Project was successfully created
- `404 Not Found`: Organization does not exist

## Listing Projects in an Organization

To list all projects in a specific organization, use:

```bash
curl -X GET "http://localhost:8000/admin/orgs/myorg123/projects"
```

Replace `myorg123` with the name of your organization.

This will return a JSON array of all projects in the specified organization.

## Creating Test Suites

To create a test suite within a project, use:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/suites" \
  -H "Content-Type: application/json" \
  -d '{"project": "myproject123", "suite": "smoke", "url": "http://myorg123.example.com/suites/smoke", "org": "myorg123"}'
```

To create another test suite, use:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/suites" \
  -H "Content-Type: application/json" \
  -d '{"project": "myproject123", "suite": "full", "url": "http://myorg123.example.com/suites/full", "org": "myorg123"}'
```

These commands create two test suites:
- `smoke` suite for quick verification tests
- `full` suite for comprehensive testing

## Creating Suite Runs

To create a suite run, use:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/runs" \
  -H "Content-Type: application/json" \
  -d '{"org": "myorg123", "project": "myproject123", "suite": "smoke", "branch": "main", "run_id": 1, "status": "SUCCESS", "tstamp": "2025-05-05T15:42:00", "url": null, "commit": null, "pass_count": null, "fail_count": null, "skip_count": null, "total_count": null, "duration_sec": null, "ignore": false}'
```

## Adding Test Results

To add test results for a suite run, use:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/projects/myproject123/suites/smoke/branches/main/runs/1/tests" \
  -H "Content-Type: application/json" \
  -d '[{"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_login_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T15:42:01", "duration_ms": 2500, "stdout": "Login successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_dashboard_load", "test_config": "default", "result": "PASS", "test_group": "ui", "tstamp": "2025-05-05T15:42:02", "duration_ms": 3000, "stdout": "Dashboard loaded successfully", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_logout_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T15:42:03", "duration_ms": 2000, "stdout": "Logout successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null}]'
```

The test results include:
- `test_login_success` - auth group, 2.5s duration
- `test_dashboard_load` - ui group, 3.0s duration
- `test_logout_success` - auth group, 2.0s duration

## Retrieving Test Run History

To view the history of a specific test case across multiple runs, use:

```bash
curl -X GET "http://localhost:8000/history/orgs/myorg123/projects/myproject123/suites/smoke/test-runs?branch=main&test_package=com.example.test&test_class=smoke&test_case=test_login_success&test_config=default" | jq -c '.[] | {run_id: .suite_run.run_id, result: .test_run.result, duration: .test_run.duration_ms, timestamp: .test_run.tstamp}' | sort -r
```

This command will show the history of the `test_login_success` test case, including:
- Run ID
- Result (PASS/FAIL)
- Duration in milliseconds
- Timestamp of the test run

The output will be sorted by timestamp in descending order (newest first). For example:

```json
{"run_id":3,"result":"PASS","duration":2500,"timestamp":"2025-05-05T15:44:01"}
{"run_id":2,"result":"PASS","duration":2500,"timestamp":"2025-05-05T15:43:01"}
{"run_id":1,"result":"PASS","duration":2500,"timestamp":"2025-05-05T15:42:01"}
```

This shows that the test has run 3 times on the main branch, all with PASS status, and consistently taking 2.5 seconds to complete.

## Development Branch Test Runs

To simulate a development flow, we can create test runs on a development branch. Here's how to create runs on the "dev" branch:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/runs" \
  -H "Content-Type: application/json" \
  -d '{"org": "myorg123", "project": "myproject123", "suite": "smoke", "branch": "dev", "run_id": 1, "status": "SUCCESS", "tstamp": "2025-05-05T16:00:00", "url": null, "commit": null, "pass_count": null, "fail_count": null, "skip_count": null, "total_count": null, "duration_sec": null, "ignore": false}'
```

And to add test results:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/projects/myproject123/suites/smoke/branches/dev/runs/1/tests" \
  -H "Content-Type: application/json" \
  -d '[{"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_login_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T16:00:01", "duration_ms": 2500, "stdout": "Login successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_dashboard_load", "test_config": "default", "result": "PASS", "test_group": "ui", "tstamp": "2025-05-05T16:00:02", "duration_ms": 3000, "stdout": "Dashboard loaded successfully", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_logout_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T16:00:03", "duration_ms": 2000, "stdout": "Logout successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null}]'
```

For the third run on dev branch, we can simulate a test failure:

```bash
curl -v -w "\nResponse code: %{response_code}\n" \
  -X POST "http://localhost:8000/tests/orgs/myorg123/projects/myproject123/suites/smoke/branches/dev/runs/3/tests" \
  -H "Content-Type: application/json" \
  -d '[{"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_login_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T16:02:01", "duration_ms": 2500, "stdout": "Login successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_dashboard_load", "test_config": "default", "result": "FAIL", "test_group": "ui", "tstamp": "2025-05-05T16:02:02", "duration_ms": 3000, "stdout": "Dashboard loaded successfully", "stderr": "Error: Failed to load dashboard data", "error_stacktrace": "java.lang.RuntimeException: Failed to load dashboard data\n    at com.example.test.DashboardTest.testDashboardLoad(DashboardTest.java:42)", "error_details": "Failed to fetch dashboard data from API", "skip_details": null},
        {"test_package": "com.example.test", "test_suite": "smoke", "test_case": "test_logout_success", "test_config": "default", "result": "PASS", "test_group": "auth", "tstamp": "2025-05-05T16:02:03", "duration_ms": 2000, "stdout": "Logout successful", "stderr": null, "error_stacktrace": null, "error_details": null, "skip_details": null}]'
```

This shows a real-world scenario where:
1. Initial runs on dev branch pass successfully
2. A later run introduces a failure in the `test_dashboard_load` test case
3. The failure includes detailed error information:
   - Error message: "Failed to load dashboard data"
   - Stack trace pointing to specific file and line
   - Detailed error description

The command will:
- `-v`: Enable verbose output to see the request/response details
- `-w "\nResponse code: %{response_code}\n"`: Show the HTTP response code
- `-X POST`: Use POST method for creating the suite
- `-H "Content-Type: application/json"`: Set the content type to JSON
- `-d`: Send the suite data as JSON

Expected responses:
- `200 OK`: Suite was successfully created (or updated)
- `404 Not Found`: Organization or project does not exist

## Listing Suites in a Project

To list all suites in a specific project, use:

```bash
curl -X GET "http://localhost:8000/tests/orgs/myorg123/projects/myproject123/suites"
```

This will return a JSON array of all suites in the specified project.
