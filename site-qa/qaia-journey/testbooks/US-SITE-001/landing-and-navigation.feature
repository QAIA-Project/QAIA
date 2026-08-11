# Feature: US-SITE-001 — what a visitor reads before deciding
# Level e2e (ADR 0008): every promise below is only observable through the rendered page.
# Derived from 01-extraction.md AC1/AC2/AC3/AC4/AC7 and 03-design.md conditions C8-C14.
Feature: The landing page decides whether a visitor tries QAIA

  Background:
    Given the site is served locally as the Pages workflow publishes it

  # C8 — open: Q1, "without scrolling" has no definition
  @QAIA-US-SITE-001-008 @AC1 @P1 @e2e @ep @low-confidence
  Scenario: The first screen states what goes in and what comes out
    # open: Q1 -- "without scrolling" depends on the window. Safe default: 1280x720, the
    # reference size already used by the suites in this repository.
    Given a visitor opens the home page in a 1280 by 720 window
    When they read without scrolling
    Then they see that a user story goes in
    And they see that a test book and runnable tests come out

  # C9 — the one that was red first, and the reason this book exists
  @QAIA-US-SITE-001-009 @AC2 @P1 @e2e @ep
  Scenario Outline: Every public page discloses the pre-alpha status
    # contract: AC2 -- on EVERY page, not only where it is comfortable to say
    Given a visitor opens "<page>"
    When they look for the project's maturity
    Then the page states that the project is pre-alpha

    Examples:
      | page              |
      | /                 |
      | /compare.html     |
      | /walkthrough.html |

  # C10
  @QAIA-US-SITE-001-010 @AC3 @P1 @e2e @ep
  Scenario: The install block can be copied as it stands
    Given a visitor opens the home page
    When they look at the installation instructions
    Then they see the marketplace command for this repository
    And they see the install command for "qaia-core"
    And they see the install command for "qaia-playwright"

  # C11
  @QAIA-US-SITE-001-011 @AC4 @P2 @e2e @ep
  Scenario: The proof claim points at the artifact behind it
    Given a visitor opens the home page
    When they follow the claim about a defect found in a stranger's repository
    Then the link targets the campaign report kept in this repository

  # C12
  @QAIA-US-SITE-001-012 @AC5 @P2 @e2e @ep
  Scenario: Every in-page navigation anchor has a target
    Given a visitor opens the home page
    When they consider each navigation anchor
    Then each one points at a section that exists on the page

  # C13
  @QAIA-US-SITE-001-013 @AC7 @P3 @e2e @ep
  Scenario Outline: Every page declares its language
    Given a visitor opens "<page>"
    When a screen reader asks the document for its language
    Then the document declares one

    Examples:
      | page              |
      | /                 |
      | /compare.html     |
      | /walkthrough.html |

  # C14
  @QAIA-US-SITE-001-014 @AC7 @P3 @e2e @ep
  Scenario: The three pages carry three different titles
    Given a visitor opens the home page, the comparison page and the walkthrough
    When they compare the browser tab titles
    Then no two pages share the same title
