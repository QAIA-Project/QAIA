# CT-AI techniques (CT-AI v2.0, istqb-design palette) exercised against a real feature (#53).
# Target: POST /api/suggest-category (examples/expense-demo/app/server.js) -- a simple
# deterministic keyword-weighted classifier, NOT a trained ML model, but a real target for
# CT-AI testing techniques: the exact confidence output can't be stated directly from any one
# input field (it depends on matched-keyword density AND total word count jointly), which is
# exactly the precondition metamorphic/CT-AI techniques target. Every scenario below was
# executed for real against the live server before being written here (curl, see
# eval/baselines/ct-ai-category-suggestion-2026-07-28.md) -- none of this is projected.

Feature: AI-style expense category suggestion

  Background:
    Given the employee is authenticated

  @US-004-AI-01 @ai-feature @P2
  Scenario: a description with clear category keywords is classified correctly
    When the employee requests a category suggestion for "taxi ride to airport for flight"
    Then the suggested category is "travel"
    And the confidence is greater than 0

  @US-004-AI-02 @ai-feature @ep @negative @P2
  Scenario: a description with no recognizable keywords falls back to "other" with zero confidence
    When the employee requests a category suggestion for "xyz qux blorp"
    Then the suggested category is "other"
    And the confidence is 0

  @US-004-AI-03 @ai-feature @negative @error-guessing @P1
  Scenario: an empty description is refused, never silently guessed
    When the employee requests a category suggestion for an empty description
    Then the request is refused with a 422 error
    And no category is guessed

  @US-004-AI-04 @ai-feature @negative @error-guessing @P1
  Scenario: adversarial-input robustness -- a non-string description degrades gracefully, never crashes
    When the employee requests a category suggestion with a numeric description instead of text
    Then the request is refused with a 422 error
    And the server does not crash or return a 5xx error

  @US-004-AI-05 @ai-feature @negative @error-guessing @P2
  Scenario: adversarial-input robustness -- an extremely long description does not crash the classifier
    When the employee requests a category suggestion for a description of 500 repeated words
    Then the request succeeds with a 200 response
    And the server does not crash or return a 5xx error

  @US-004-AI-06 @ai-feature @negative @error-guessing @P1
  Scenario: an unauthenticated request is refused before any classification happens
    When an unauthenticated request asks for a category suggestion
    Then the request is refused with a 401 error

  @US-004-AI-07 @metamorphic @P2
  Scenario: consistency / back-to-back -- the same input yields the same output across repeated calls
    When the employee requests a category suggestion for "dinner at restaurant" twice in a row
    Then both responses have the same category
    And both responses have the same confidence

  @US-004-AI-08 @metamorphic @P2
  Scenario: metamorphic relation -- diluting a matched description with unrelated words strictly lowers confidence, never raises it
    Given a category suggestion for "dinner at restaurant" has confidence 0.67
    When the employee requests a category suggestion for the same text padded with unrelated words
    Then the new confidence is lower than 0.67
    And the suggested category is unchanged
