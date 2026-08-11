# Fixture ROUGE de check_test_levels.py -- ce fichier DOIT echouer le controle.
# Il est hors du perimetre du controle (EXCLUDED_MARKERS) et n'est lu que par
# selfcheck_test_levels.py, qui verifie que les deux violations d'ADR 0008 sont bien vues.
# Ne pas "corriger" ce fichier : un depot dont la fixture rouge devient verte a perdu sa preuve.
Feature: Fixture rouge des niveaux de test

  @QAIA-FIX-001 @AC1 @P1 @ep
  Scenario: Aucune etiquette de niveau -- doit etre signale
    Given un scenario sans @e2e ni @api
    When le controle passe
    Then il signale l'absence

  @QAIA-FIX-002 @AC1 @P1 @e2e @api @ep
  Scenario: Deux etiquettes de niveau -- doit etre signale
    Given un scenario portant @e2e et @api
    When le controle passe
    Then il signale le doublon

  @QAIA-FIX-003 @AC1 @P1 @api @ep
  Scenario: Une seule etiquette -- ne doit PAS etre signale
    Given un scenario portant @api seul
    When le controle passe
    Then il ne dit rien de ce scenario
