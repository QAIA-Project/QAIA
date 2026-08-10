Feature: Scenario Template et Scenarios (alias officiels)

  Scenario Template: refus de <amount>
    Given a report of <amount>
    Then the submission is refused

    Scenarios:
      | amount |
      | -1     |
      | 0      |
