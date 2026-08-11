# Fixture de check_nl_projection.py -- le Gherkin de reference.
# Les fichiers *.md a cote sont des rendus VOLONTAIREMENT divergents, sauf conforme.md.
# Ne pas "corriger" ce dossier : un depot dont les fixtures rouges deviennent vertes a perdu sa preuve.
Feature: Fixture du rendu en langage naturel

  Background:
    Given the system is reset

  @QAIA-FIXNL-001 @AC1 @P1 @api @ep
  Scenario: A valid request is accepted
    Given an authenticated caller
    When they POST /things with a valid body
    Then the response status is 201

  @QAIA-FIXNL-002 @AC1 @P2 @api @negative @boundary
  Scenario Outline: An out-of-range size is refused
    Given an authenticated caller
    When they POST /things with size "<size>"
    Then the response status is 400

    Examples:
      | size |
      | 0    |
      | 999  |
