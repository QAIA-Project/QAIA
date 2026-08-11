Feature: TaskAPI contract regression — contract-probe findings

  @QAIA-CP-001 @negative @api
  # contract: fixture/taskapi/README.md, "What this API promises" item 2 — "GET /tasks/:id
  # returns the task if it exists, or HTTP 404 if it does not — for any input, malformed or
  # not. It never returns a 5xx."
  Scenario: A nonexistent task id returns 404, never a 500
    Given the TaskAPI fixture is running with no task at id 999
    When a client sends "GET /tasks/999"
    Then the response status is 404
    And the response is not a 5xx status
