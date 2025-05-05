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
