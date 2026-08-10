Feature: Doc String

  Scenario: le corps de la reponse est verifie
    Given the endpoint is called
    Then the response body is:
      """
      { "status": "refused", "reason": "over the limit" }
      """
