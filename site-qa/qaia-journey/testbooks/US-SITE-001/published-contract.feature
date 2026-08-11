# Feature: US-SITE-001 — what the published site promises over HTTP
# Level api (ADR 0008): every promise below is observable with an HTTP client, no browser.
# Derived from 01-extraction.md AC5/AC6 and 03-design.md conditions C1-C7.
Feature: The published site answers what it declares

  Background:
    Given the site is assembled the way the Pages workflow assembles it

  # C1 — every declared URL answers
  @QAIA-US-SITE-001-001 @AC5 @P1 @api @ep
  Scenario Outline: Every declared URL is served
    # contract: pages.yml assembles _site from site/ and examples/expense-demo/static-demo/
    When a client requests "<path>"
    Then the response status is 200

    Examples:
      | path             |
      | /                |
      | /compare.html    |
      | /walkthrough.html|
      | /demo/           |
      | /llms.txt        |
      | /robots.txt      |
      | /sitemap.xml     |

  # C2 — the refusal path
  @QAIA-US-SITE-001-002 @AC5 @P2 @api @negative @error-guessing
  Scenario: An address the site never published is not served as a page
    # contract: AC5 -- only declared destinations resolve
    When a client requests "/this-page-was-never-published.html"
    Then the response status is 404

  # C3 — robots points at a sitemap that exists
  @QAIA-US-SITE-001-003 @AC6 @P2 @api @ep
  Scenario: robots.txt points at a sitemap that answers
    # contract: AC6 -- machine readers are served
    When a client requests "/robots.txt"
    Then the response status is 200
    And the body declares a sitemap whose URL answers 200

  # C4 — the consistency nobody reads across three files
  @QAIA-US-SITE-001-004 @AC6 @P1 @api @negative @ep
  Scenario: The sitemap lists exactly the published entry points
    # contract: AC6 -- neither more nor less
    When a client requests "/sitemap.xml"
    Then the response status is 200
    And every URL it lists is served
    And every published entry point is listed in it

  # C5 — content types
  @QAIA-US-SITE-001-005 @AC5 @P3 @api @ep
  Scenario Outline: Each HTML page is served as HTML
    # contract: AC5 -- a page served as text/plain is a page browsers will not render
    When a client requests "<path>"
    Then the response content type is "text/html"

    Examples:
      | path             |
      | /                |
      | /compare.html    |
      | /walkthrough.html|

  # C6 — llms.txt carries something
  @QAIA-US-SITE-001-006 @AC6 @P3 @api @boundary
  Scenario: llms.txt is served and is not empty
    # contract: AC6 -- an empty llms.txt answers 200 and serves nobody
    When a client requests "/llms.txt"
    Then the response status is 200
    And the body is longer than 200 characters

  # C7 — the second assembly source
  @QAIA-US-SITE-001-007 @AC5 @P1 @api @negative @ep
  Scenario: The demo is served from the second assembly source
    # contract: pages.yml -- _site/demo/ comes from examples/expense-demo/static-demo/
    When a client requests "/demo/index.html"
    Then the response status is 200
    And the body mentions the demo application
