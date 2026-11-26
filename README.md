# Python + Pytest QA Automation Framework

[![CI](https://github.com/ManikandanK-QA/python-pytest-qa-automation/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ManikandanK-QA/python-pytest-qa-automation/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-9.2-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.65-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A layered **pytest** framework for UI and REST API automation, written the way a
maintained suite is written in a team: page objects without assertions, typed
fixtures with real teardown, pydantic contracts on every API response, validated
configuration, parallel-safe tests, and CI that separates layers instead of
running everything against every browser.

It runs against stable public demo systems — **SauceDemo** (sign-in, catalogue,
cart, checkout) and **Restful Booker** (token auth, CRUD) — so a fresh clone runs
with no secrets, accounts or local services.

## What this demonstrates

- **Layer isolation by marker** — `pytest -m api` runs 11 REST tests without
  launching a browser; `pytest -m ui` runs the browser suite; `smoke` is the
  pre-merge gate.
- **Page Object Model with a clean contract** — page objects expose intent and
  locators; every assertion lives in a spec, so a failure points at the test line.
- **Fixture-owned data** — `booking_factory` creates records on demand and deletes
  them in teardown, even when a test fails midway.
- **Contract validation, not just status codes** — pydantic models parse each
  response before assertions run, and a drifted field fails with its exact path.
- **Configuration that fails fast** — `pydantic-settings` validates URLs, log level
  and timeout at startup.
- **Correct parallel execution** — `pytest-xdist` works without serial markers
  because tests are independent by construction and auth state is per worker.
- **Real failure diagnostics** — full-page screenshot and page HTML attached to
  Allure; Playwright trace and screenshot retained in CI on failure.
- **Cross-browser capable** — the same specs run on Chromium, Firefox and WebKit;
  CI runs all three.

## Stack

| Concern | Tool |
| --- | --- |
| Test runner | pytest 9 |
| Browser automation | Playwright for Python 1.65 + `pytest-playwright` |
| API client | `httpx` |
| Contracts and settings | pydantic 2 + `pydantic-settings` |
| Test data | `faker` factories + typed static data |
| Reporting | Allure, JUnit XML, Playwright traces |
| Quality | Ruff (lint + format), mypy (strict) |
| Parallelism | `pytest-xdist` |
| CI | GitHub Actions, Python 3.13, Allure published to GitHub Pages |

## Architecture

```
tests/
  conftest.py            settings, API client, booking factory, reporting hooks
  ui/                    browser fixtures, auth state, UI specs
  api/                   REST specs

src/qa_portfolio/
  config.py              validated environment (pydantic-settings)
  pages/                 page objects + shared components
  api/                   ApiClient, BookingApi, typed errors
  models/                pydantic response contracts
  data/                  static data + synthetic factories
  utils/                 structured logging, shared paths
```

Full design notes: [docs/architecture.md](docs/architecture.md) ·
Test approach: [docs/test-strategy.md](docs/test-strategy.md) ·
Pipeline: [docs/ci.md](docs/ci.md).

## Quick start

Requirements: **Python 3.12+** and pip.

```bash
git clone https://github.com/ManikandanK-QA/python-pytest-qa-automation.git
cd python-pytest-qa-automation

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

python -m pip install -e ".[dev]"
python -m playwright install chromium

python -m pytest
```

Configuration is optional — defaults point at the public demos:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

## Commands

| Command | Runs |
| --- | --- |
| `python -m pytest` | full suite (13 UI + 11 API) |
| `python -m pytest -m smoke` | fast pre-merge subset |
| `python -m pytest -m ui` | browser suite only |
| `python -m pytest -m api` | REST suite only, no browser |
| `python -m pytest -n auto` | full suite in parallel |
| `python -m pytest -m ui --browser firefox` | UI suite on another engine |
| `python -m pytest tests/api/test_bookings.py -k partial -vv` | one test, verbose |
| `ruff check .` | lint |
| `ruff format --check .` | formatting gate |
| `mypy` | strict type check |
| `allure serve allure-results` | open the last run's Allure report (needs Java) |

## Coverage

| Layer | Scenarios |
| --- | --- |
| Authentication | valid sign-in; locked-out user; wrong password; missing username; missing password |
| Catalogue | six products listed; ascending price sort; add/remove with badge synchronisation |
| Cart | contents reflect additions; removal updates count; continue shopping |
| Checkout | end-to-end purchase with confirmation; mandatory postal code |
| API auth | token issued; invalid credentials rejected (including the service's HTTP 200 + reason quirk) |
| API CRUD | create/read; name filter; full update; partial update; delete then verify 404 |
| API negative | unknown id → 404; write without token → 403; invalid create payload → 500 |

Every module is tagged `ui`/`api` and `regression`; the highest-value cases are
also tagged `smoke`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `BASE_URL` | `https://www.saucedemo.com` | UI target |
| `API_BASE_URL` | `https://restful-booker.herokuapp.com` | REST target |
| `SAUCE_USERNAME` / `SAUCE_PASSWORD` | `standard_user` / `secret_sauce` | UI credentials |
| `BOOKER_USERNAME` / `BOOKER_PASSWORD` | `admin` / `password123` | API credentials |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `REQUEST_TIMEOUT` | `15` | per-request timeout, seconds |

Values are parsed by `src/qa_portfolio/config.py`. An invalid URL or log level
stops the run with a field-level message before any browser launches. `.env` and
`.auth/` are git-ignored; only `.env.example` is committed.

## Reporting

Each run produces:

- **Allure results** — `allure-results/` (cleaned per run to avoid duplicate
  history), rendered by CI and published from `gh-pages`.
- **JUnit XML** — `reports/junit.xml`, for CI dashboards and test-management tools.
- **Playwright artefacts** — traces and screenshots in `test-results/`, retained
  on failure.

A UI failure also attaches the full-page screenshot and page HTML directly to the
Allure result, so the report is enough to triage without the CI artifact.

## CI/CD

```
quality (ruff format --check, ruff check, mypy)
   ├─ ui: chromium
   ├─ ui: firefox
   ├─ ui: webkit
   └─ api
        └─ publish (main only) → merged Allure report → gh-pages
```

The API job installs no browser. Each UI job installs only its own engine. The
workflow also runs nightly, so drift in the demo targets is found before a human
notices. Details and troubleshooting: [docs/ci.md](docs/ci.md).

## Design decisions

**Why `pytest-playwright` instead of wiring `sync_playwright()` by hand.** The
plugin already owns browser lifecycle, per-test contexts, tracing, screenshots,
video and cross-browser parametrisation. Re-implementing that adds code without
adding signal; this framework builds on top of it.

**Why pydantic contracts.** Status-only assertions pass when a field silently
changes type or disappears. Parsing at the boundary turns schema drift into a
message naming the field, before an assertion produces a misleading diff.

**Why fixture teardown instead of a serial lifecycle.** A serial class lets one
failure cascade into every later test and leaks records when a step fails. A
per-test factory is independent, parallel-safe and self-cleaning.

**Why per-worker auth state.** `storageState` removes a UI login from every test,
but one shared file would race under `xdist`. The filename includes
`PYTEST_XDIST_WORKER`, and the directory is git-ignored because a session is a
credential.

**Why warnings are errors — with one documented exception.** Warnings hide real
signal. The single ignore is a pytest 9 deprecation emitted by pytest-playwright's
own `base_url` fallback fixture; the rationale is written next to the filter so it
does not become a dumping ground.

**Why no retries.** A test that only passes on retry is a defect. The suite is
deterministic; retries would hide exactly the flakiness this repository is
supposed to demonstrate an engineer can find.

## Verified locally

| Check | Result |
| --- | --- |
| `ruff check .` / `ruff format --check .` | clean |
| `mypy` | no issues in 33 source files |
| `python -m pytest -m api` | **11/11 passed** in 10.1s |
| `python -m pytest -m ui` | **13/13 passed** in 22.4s |
| `python -m pytest -n auto` | **24/24 passed** in 13.0s |
| Failure-artefact path | verified with a deliberately failing probe: screenshot + page HTML attached to Allure |
| Environment | Windows 11 · Python 3.15.2 · pytest 9.2.0 · Playwright 1.65.2 |
| Verified on | 26 November 2026 |

## Limitations

- Both targets are third-party public demos; they can change or go offline.
- Restful Booker is a shared instance. Tests assert only on records they created,
  but other users' bookings are visible in list responses.
- `allure serve` and report generation need a JRE locally; tests do not.
- CI runs Python 3.13 while this machine verified on 3.15; the code targets 3.12+
  and uses no version-specific behaviour.
- Visual regression, performance and security testing are out of scope here and
  live in the companion repositories.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

The pytest framework itself ([pytest-dev/pytest](https://github.com/pytest-dev/pytest),
MIT) was studied for fixture, marker and reporting internals. Every line in this
repository is original; no third-party framework code or test suite is vendored.

## Author

**Manikandan Kandasamy** — Senior Software Test Engineer
[GitHub](https://github.com/ManikandanK-QA) · [Email](mailto:manikandan.auto.qa@gmail.com)
