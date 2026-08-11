# Worked demonstration — oracle-generate on a card-validation US.
# The US only said "validate the card number". The Luhn oracle supplied the
# grounded valid/invalid cases and their correct expected results — each tagged
# @oracle:luhn and cited, never guessed. Negative-path coverage (ADR 0001) is
# raised without fabrication because the cases come from the standard.

Feature: Payment card number validation

  Background:
    Given the checkout page is open

  @QAIA-PAY-001 @AC1 @P1 @oracle:luhn @e2e
  # oracle: ISO/IEC 7812 Luhn mod-10 — standard valid test PAN
  Scenario: A Luhn-valid Visa number is accepted
    When the customer enters card number "4111 1111 1111 1111"
    Then the number is accepted as valid

  @QAIA-PAY-002 @AC1 @P1 @negative @oracle:luhn @e2e @boundary
  # oracle: Luhn — same digits, check digit off by one
  Scenario: A number failing the Luhn checksum is rejected
    When the customer enters card number "4111 1111 1111 1112"
    Then the number is rejected with a "invalid card number" error

  @QAIA-PAY-003 @AC1 @P2 @negative @oracle:luhn @e2e
  # oracle: Luhn — Amex is 15 digits; 16 is wrong length for the network
  Scenario Outline: Numbers with a wrong length for their network are rejected
    When the customer enters card number "<pan>"
    Then the number is rejected with a "invalid card number" error
    Examples:
      | pan                 |
      | 3782 822463 1000    |
      | 4111 1111 1111 111  |
      | 4111 1111 1111 11111 |

  @QAIA-PAY-004 @AC1 @P2 @negative @oracle:luhn @e2e
  # oracle: Luhn — non-digit and empty inputs
  Scenario Outline: Malformed card inputs are rejected
    When the customer enters card number "<pan>"
    Then the number is rejected with a "invalid card number" error
    Examples:
      | pan                 |
      | 4111-1111-XXXX-1111 |
      |                     |
      | 0000 0000 0000 0000 |

  @QAIA-PAY-005 @AC1 @P3 @negative @oracle:luhn @low-confidence @e2e
  # oracle: Luhn valid but IIN unknown — [open]: does the US require IIN/network check? Q1
  Scenario: A Luhn-valid number with an unassigned issuer prefix
    When the customer enters card number "9999 9999 9999 9995"
    Then the number is rejected as an unrecognized issuer
