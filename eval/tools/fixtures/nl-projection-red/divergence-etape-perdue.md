---
language: en
source: base.feature
---

# Fixture

### QAIA-FIXNL-001 · A valid request is accepted

Requirement: AC1

**Preconditions**

1. the system is reset
2. an authenticated caller

**Action**

3. they POST /things with a valid body

### QAIA-FIXNL-002-e1 · An out-of-range size is refused

Requirement: AC1

**Preconditions**

1. the system is reset
2. an authenticated caller

**Action**

3. they POST /things with size "0"

**Expected result**

4. the response status is 400

### QAIA-FIXNL-002-e2 · An out-of-range size is refused

Requirement: AC1

**Preconditions**

1. the system is reset
2. an authenticated caller

**Action**

3. they POST /things with size "999"

**Expected result**

4. the response status is 400
