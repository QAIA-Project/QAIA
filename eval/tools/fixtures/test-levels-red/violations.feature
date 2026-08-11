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

  @QAIA-FIX-004 @AC1 @P1 @e2e @use-case
  Scenario: Une etiquette retiree -- doit etre signale
    Given un scenario portant @use-case, retiree par testbook-generate
    When le controle passe
    Then il signale l'etiquette retiree

  @QAIA-FIX-005 @AC1 @P1 @api @ep
  # Un commentaire entre la ligne de tags et le Scenario -- forme REELLE, employee par
  # contract-probe et par tout le cahier booking-api-demo. Ajoute le 2026-08-11 apres qu'une
  # campagne mutation ait montre que neutraliser la remontee au-dessus d'un commentaire ne
  # faisait rougir AUCUNE auto-verification : le controle serait devenu aveugle a la moitie
  # des cahiers du depot sans que rien ne le dise.
  Scenario: Une etiquette separee du scenario par un commentaire -- ne doit PAS etre signale
    Given un scenario dont les tags sont suivis d'un commentaire
    When le controle passe
    Then il ne dit rien de ce scenario
