Feature: Rule et Example (Gherkin 6)

  Rule: un rapport sous le seuil ne demande qu'une approbation

    Example: sous le seuil
      Given a report of 100
      When it is submitted
      Then only the manager approves
