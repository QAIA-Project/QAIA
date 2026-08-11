---
language: en
source: landing-and-navigation.feature, published-contract.feature
---

# QAIA site — US-SITE-001: the test book in plain language

Projection of the two feature files. Same scenarios, same steps, same order — readable without knowing Gherkin. The .feature files stay the source of truth; this file is checked against them step by step, and a single divergence fails the build.

### QAIA-US-SITE-001-008 · The first screen states what goes in and what comes out

Requirement: AC1 · Priority: 1 (highest) · Level: end-to-end (user interface) · Technique: equivalence partitioning · Rests on an unanswered question

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens the home page in a 1280 by 720 window

**Action**

3. they read without scrolling

**Expected result**

4. they see that a user story goes in
5. they see that a test book and runnable tests come out

### QAIA-US-SITE-001-009-e1 · Every public page discloses the pre-alpha status

Requirement: AC2 · Priority: 1 (highest) · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/"

**Action**

3. they look for the project's maturity

**Expected result**

4. the page states that the project is pre-alpha

### QAIA-US-SITE-001-009-e2 · Every public page discloses the pre-alpha status

Requirement: AC2 · Priority: 1 (highest) · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/compare.html"

**Action**

3. they look for the project's maturity

**Expected result**

4. the page states that the project is pre-alpha

### QAIA-US-SITE-001-009-e3 · Every public page discloses the pre-alpha status

Requirement: AC2 · Priority: 1 (highest) · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/walkthrough.html"

**Action**

3. they look for the project's maturity

**Expected result**

4. the page states that the project is pre-alpha

### QAIA-US-SITE-001-010 · The install block can be copied as it stands

Requirement: AC3 · Priority: 1 (highest) · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens the home page

**Action**

3. they look at the installation instructions

**Expected result**

4. they see the marketplace command for this repository
5. they see the install command for "qaia-core"
6. they see the install command for "qaia-playwright"

### QAIA-US-SITE-001-011 · The proof claim points at the artifact behind it

Requirement: AC4 · Priority: 2 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens the home page

**Action**

3. they follow the claim about a defect found in a stranger's repository

**Expected result**

4. the link targets the campaign report kept in this repository

### QAIA-US-SITE-001-012 · Every in-page navigation anchor has a target

Requirement: AC5 · Priority: 2 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens the home page

**Action**

3. they consider each navigation anchor

**Expected result**

4. each one points at a section that exists on the page

### QAIA-US-SITE-001-013-e1 · Every page declares its language

Requirement: AC7 · Priority: 3 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/"

**Action**

3. a screen reader asks the document for its language

**Expected result**

4. the document declares one

### QAIA-US-SITE-001-013-e2 · Every page declares its language

Requirement: AC7 · Priority: 3 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/compare.html"

**Action**

3. a screen reader asks the document for its language

**Expected result**

4. the document declares one

### QAIA-US-SITE-001-013-e3 · Every page declares its language

Requirement: AC7 · Priority: 3 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens "/walkthrough.html"

**Action**

3. a screen reader asks the document for its language

**Expected result**

4. the document declares one

### QAIA-US-SITE-001-014 · The three pages carry three different titles

Requirement: AC7 · Priority: 3 · Level: end-to-end (user interface) · Technique: equivalence partitioning

**Preconditions**

1. the site is served locally as the Pages workflow publishes it
2. a visitor opens the home page, the comparison page and the walkthrough

**Action**

3. they compare the browser tab titles

**Expected result**

4. no two pages share the same title

### QAIA-US-SITE-001-001-e1 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e2 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/compare.html"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e3 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/walkthrough.html"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e4 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/demo/"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e5 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/llms.txt"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e6 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/robots.txt"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-001-e7 · Every declared URL is served

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/sitemap.xml"

**Expected result**

3. the response status is 200

### QAIA-US-SITE-001-002 · An address the site never published is not served as a page

Requirement: AC5 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: error guessing

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/this-page-was-never-published.html"

**Expected result**

3. the response status is 404

### QAIA-US-SITE-001-003 · robots.txt points at a sitemap that answers

Requirement: AC6 · Priority: 2 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/robots.txt"

**Expected result**

3. the response status is 200
4. the body declares a sitemap whose URL answers 200

### QAIA-US-SITE-001-004 · The sitemap lists exactly the published entry points

Requirement: AC6 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/sitemap.xml"

**Expected result**

3. the response status is 200
4. every URL it lists is served
5. every published entry point is listed in it

### QAIA-US-SITE-001-005-e1 · Each HTML page is served as HTML

Requirement: AC5 · Priority: 3 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/"

**Expected result**

3. the response content type is "text/html"

### QAIA-US-SITE-001-005-e2 · Each HTML page is served as HTML

Requirement: AC5 · Priority: 3 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/compare.html"

**Expected result**

3. the response content type is "text/html"

### QAIA-US-SITE-001-005-e3 · Each HTML page is served as HTML

Requirement: AC5 · Priority: 3 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/walkthrough.html"

**Expected result**

3. the response content type is "text/html"

### QAIA-US-SITE-001-006 · llms.txt is served and is not empty

Requirement: AC6 · Priority: 3 · Level: API (service contract) · Technique: boundary values

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/llms.txt"

**Expected result**

3. the response status is 200
4. the body is longer than 200 characters

### QAIA-US-SITE-001-007 · The demo is served from the second assembly source

Requirement: AC5 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the site is assembled the way the Pages workflow assembles it

**Action**

2. a client requests "/demo/index.html"

**Expected result**

3. the response status is 200
4. the body mentions the demo application

