Feature: json-server alpha v1 — regressions from contract probing (README.target.md)

  Background:
    Given json-server is running on "http://localhost:3010" with the README example db.json

  @QAIA-CP-001 @negative @api
  # contract: README.target.md, "## Routes" line 116 — "PATCH /profile" (partial update of the
  # singular resource; same route family as "PATCH  /posts/:id", line 107, which merges correctly)
  Scenario: PATCH /profile merges the body into the profile instead of nesting the old content
    Given "GET /profile" returns {"name":"typicode"}
    When a client sends "PATCH /profile" with JSON body {"age":3}
    Then the response status is 200
    And "GET /profile" returns {"name":"typicode","age":3}
    And the profile has no "item" key
    # observed: {"item":{"name":"typicode"},"age":3}

  @QAIA-CP-002 @negative @api
  # contract: README.target.md, "## Notable differences with v0.17" line 200 —
  # "`id` is always a string and will be generated for you if missing"
  Scenario: POST with a numeric id does not store a non-string id
    When a client sends "POST /posts" with JSON body {"id":3,"title":"numeric id"}
    Then the stored record's "id" is a string
    And "GET /posts/3" returns status 200 with that record
    # observed: 201 with {"id":3,...}; the record is listed by GET /posts with numeric id 3,
    # but GET /posts/3 and DELETE /posts/3 return 404 (also reproduced with id 42, null, true,
    # and on POST /comments with id 7)

  @QAIA-CP-003 @negative @api
  # contract: README.target.md, "## Delete" lines 183-184 — "DELETE /posts/1" and
  # "DELETE /posts/1?_dependent=comments" (documented by example only; that dependents are
  # deleted is inferred from the option's name — confirmed: the option has no observable effect)
  Scenario: DELETE with _dependent=comments also deletes the post's comments
    Given comments "1" and "2" have postId "1"
    When a client sends "DELETE /posts/1?_dependent=comments"
    Then the response status is 200
    And "GET /comments/1" returns status 404
    And "GET /comments/2" returns status 404
    # observed: both comments still exist with "postId": null — identical to plain DELETE /posts/1
