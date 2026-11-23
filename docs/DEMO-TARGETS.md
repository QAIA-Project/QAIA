# Demo & practice targets for QAIA

Vetted catalog of public apps and GitHub lists to exercise QAIA on real software. `probe` cites this file as its list of authorised targets. The Security, Perf, A11y and Visual columns date from the 37-skill catalogue: those disciplines left the product on 2026-10-26, and the columns stay as information on what each target permits. **Golden rule:** *explore* on shared public demos; run *security scans and load tests only on self-hosted* instances (Docker/npm/VPS) — shared demos forbid them, and offline CI can't reach them. Self-hosting (a VPS such as **OVH**, Docker, or a local server) lifts both limits.

## Recommended pairing

- **Healthcare-shaped: OpenEMR** — GPL-3.0, very active (release 8.2.0, Jul 2026). Rich clinical UI, **REST + FHIR R4 API with Swagger**, multi-role demo creds (`admin`/`pass`), official Docker for self-host. Demos: `one.openemr.io/d/openemr` (reset daily 08:30 UTC). Medical US ideas: appointment booking, prescription with allergy check, FHIR Patient/Observation OAuth2 flow — test data = synthetic patients (Synthea-style), never real.
- **Generalist: Practice Software Testing (Toolshop)** — modern Angular SPA + Swagger API + a deliberately buggy variant. UI `practicesoftwaretesting.com`, API `api.practicesoftwaretesting.com`. ⚠ repo license is now restrictive for self-hosting — verify before hosting.

## Coverage matrix (verified via project READMEs, 2026-07)

| Target | Self-host | UI | API | Mobile | Security | Perf | A11y | Visual |
|---|---|---|---|---|---|---|---|---|
| OpenEMR | ✅ Docker | ✅ | ✅ REST+FHIR | responsive | self-host only | self-host only | ✅ | ✅ |
| Practice Software Testing | ⚠ license | ✅ | ✅ | responsive | demo forbids | demo forbids | ✅ | ✅ (buggy variant) |
| Restful-Booker-Platform | ✅ Docker | ✅ | ✅✅ | responsive | self-host | self-host | ⚠ | ⚠ |
| OWASP Juice Shop | ✅ Docker | ✅ | ✅ | responsive | ✅✅ (only one allowing pentest) | self-host | ⚠ | ⚠ |
| SauceDemo | ❌ | ✅ | ❌ | +native demo app | ❌ | ❌ | ⚠ | ✅ |
| the-internet | ✅ Docker | ✅✅ edge cases | ❌ | ❌ | ❌ | ❌ | ⚠ | ⚠ |
| DemoBlaze | ❌ | ✅ e-commerce | ⚠ undocumented | ❌ | ❌ | demo forbids | ⚠ | ⚠ |
| OctoPerf Pet Store | ❌ | ✅ (JPetStore-style) | ❌ | ❌ | ❌ | demo forbids — self-host a JPetStore clone for a real k6 run | ❌ | ❌ |
| Deque Broken Workshop | ❌ | ✅ (intentionally broken) | ❌ | ❌ | ❌ | ❌ | ✅✅ purpose-built (also see W3C Before-After Demo) | ❌ |

Native mobile: SauceLabs **My Demo App** (React Native, OSS) is the go-to real-native target (needs Appium — out of QAIA v1 scope, D100).

## Newly suggested (2026-07-30, unverified)

Sourced from a list shared by the founder (LinkedIn post). **Not yet explored live** — listed
here as candidates for a future campaign wave, not confirmed against the golden rule or
checked for reachability/licensing. Verify before using for anything beyond UI exploration.

| Target | Type | Notes |
|---|---|---|
| LambdaTest e-commerce playground (`ecommerce-playground.lambdatest.io`) | UI functional | E-commerce (OpenCart-based demo) |
| Tricentis Demo Web Shop (`demowebshop.tricentis.com`) | UI functional | E-commerce |
| DemoQA (`demoqa.com`) | UI functional | Widgets/forms/interactions grab-bag, popular for locator practice |
| UI Testing Playground (`uitestingplayground.com`) | UI functional | Deliberately tricky widgets (AJAX delays, shifting buttons, overlapped elements) |
| Tocha Solutions (`qa.tochasolutions.com`) | UI functional | Unfamiliar source, verify legitimacy/scope before using |
| RESTful-api.dev | API | Simple public REST API for CRUD practice |
| JSONPlaceholder (`jsonplaceholder.typicode.com`) | API | Fake REST API, canonical for API-testing tutorials |
| RandomUser.me | API | Random user data generator API |

Already in the verified catalog above under different names: SauceDemo, DemoBlaze, the-internet
(Herokuapp), Practice Software Testing/Toolshop.

## GitHub lists that catalog targets

| Repo | What it lists |
|---|---|
| `BMayhew/awesome-sites-to-test-on` | ~100+ demo sites by domain (Web/API/Security/Perf) — ServeRest, PlayPI, DemoBlaze, DemoQA, Sunny Meadows |
| `OWASP/www-project-vulnerable-web-applications-directory` (VWAD) | ~150+ vulnerable apps, `offline` tag = self-hostable — crAPI, VAmPI, DVGA, Broken Crystals, NodeGoat, PyGoat |
| `vavkamil/awesome-vulnerable-apps`, `kaiiyer/awesome-vulnerable` | vulnerable web + mobile + k8s labs (Vulhub, DVIA, InsecureBankv2) |
| `grafana/awesome-k6` | perf tooling + **QuickPizza** self-hosted load-test demo |
| `brunopulis/awesome-a11y` | a11y resources (tooling); for a target, use the W3C Before-After Demo (BAD) |

## Where QAIA and its targets can be hosted

- **QAIA itself** (skills/plugins): nothing to host — lives on GitHub, installed into the user's Claude session.
- **Targets under test**: a VPS (OVH, etc.), Docker, or Codespaces for a full app with backend/API — required for security & load testing.
- **A public QAIA showcase/doc**: GitHub Pages (static) suffices; GitHub Actions runs the CI + Playwright suite; GitHub itself does not host a persistent backend.

See `examples/medibook/` for a fully worked, executable example (local self-hosted app + POM automation, 26 tests / 32 executions, all green).
