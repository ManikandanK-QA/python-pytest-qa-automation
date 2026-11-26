# Architecture

## Goals

1. Tests read as behaviour, not plumbing.
2. UI and API suites are independent: API tests never launch a browser.
3. Failures are diagnosable from CI output and Allure alone.
4. A new engineer can add a test without editing framework internals.
5. The suite stays parallel-safe on a shared public demo service.

## Layer map

```
tests/                        executable scenarios (assertions live here)
  conftest.py                 settings, API client, booking factory, reporting hooks
  ui/conftest.py              browser session, auth state, failure artefacts
  ui/test_*.py
  api/test_*.py

src/qa_portfolio/
  config.py                   pydantic-settings, validated once
  pages/                      page objects (intent + locators, no assertions)
    components/               shared fragments (header, cart badge)
  api/                        ApiClient, BookingApi, typed errors
  models/                     pydantic contracts for API responses
  data/                       typed static data + Faker factories
  utils/                      logging, shared paths
```

Dependencies point downward only: tests → pages/api/data → models/config/utils.
No page object imports a spec, and no API class knows about the browser.

## Why pytest-playwright

The alternative is writing `sync_playwright()` setup and teardown in a fixture.
`pytest-playwright` already provides:

| Capability | Provided by |
| --- | --- |
| browser/context/page lifecycle per test | fixtures (`browser`, `context`, `page`) |
| trace, screenshot and video on failure | `--tracing`, `--screenshot`, `--video` |
| cross-browser runs | `--browser firefox --browser webkit` |
| per-test context overrides | `@pytest.mark.browser_context_args(...)` |

Re-implementing those would add code without adding signal. The framework
builds on top of them instead of around them.

## Fixture topology

| Fixture | Scope | Responsibility |
| --- | --- | --- |
| `settings` | session | validated environment, parsed once |
| `api_client` | session | one httpx connection pool, request logging |
| `booking_api` | session | endpoint object with lazily cached token |
| `booking_factory` | function | creates bookings, deletes them in teardown |
| `auth_state` | session | one UI login → `storageState` file |
| `browser_context_args` | session | injects base URL + reused session |
| `capture_failure_artifacts` | function (autouse, UI only) | screenshot + page source on failure |

`booking_factory` is the important one. A test asks for data, not for setup:

```python
created = booking_factory({"firstname": "Manikandan"})
fetched = booking_api.get(created.bookingid)
```

Teardown deletes every id the factory created, including when the test fails
halfway. That removes the serial lifecycle where one failure poisons the rest,
and it prevents orphaned records on the shared demo service.

## Authentication flow

```
auth_state (session, once per xdist worker)
  └─ LoginPage.goto() → login() → wait for /inventory.html
     └─ context.storage_state('.auth/standard-user-<worker>.json')

browser_context_args (session)
  └─ { base_url, storage_state } → every context starts signed in

test_login.py
  └─ @pytest.mark.browser_context_args(storage_state=None)
     └─ genuinely signed out, because that is the behaviour under test
```

The state file is per worker (`PYTEST_XDIST_WORKER`), because two workers
writing one path would race. It is git-ignored: a session is a credential, so
CI regenerates it instead of caching it.

## API design

`ApiClient` owns transport: base URL, timeouts, JSON decoding, duration logging.
`BookingApi` owns domain: paths, payloads, token header, response contracts.
Specs own assertions.

Response contracts are pydantic models:

```python
booking = client.parse(response, Booking)
```

A drifted field fails with the exact path and message before any assertion runs:

```
Contract violation for GET https://.../booking/42 (status 200):
  - totalprice: Input should be a valid integer, got a string
```

That is the difference between "expected True, received False" and knowing
which field changed type.

Raw responses stay available (`get_response`, `authenticate_response`,
`replace`, `delete`) so negative tests can assert 403/404/500 without a helper
raising first.

## Parallelism

`pytest-xdist` is supported without special markers because tests are
independent by construction:

- Each API test creates and deletes its own bookings.
- UI tests navigate from the catalogue rather than relying on a previous test.
- Session fixtures are worker-local (one auth file per worker, one HTTP client
  per worker).
- No test asserts on global state, such as the total number of bookings.

`-n auto` is therefore safe in CI and documented as the default there.

## Failure handling

- Invalid configuration fails at import time with a field-level message.
- Endpoint helpers that must succeed raise `ApiRequestError` with status and a
  truncated body.
- Contract mismatches raise `ApiContractError` with the field path.
- A UI failure attaches a full-page screenshot and the page HTML to Allure;
  Playwright's trace and screenshot land in `test-results/` for the CI artifact.

## Extension points

| Need | Where |
| --- | --- |
| New page | `src/qa_portfolio/pages/`, extend `BasePage` |
| New API resource | `src/qa_portfolio/api/` + `models/` contract |
| New test data shape | `src/qa_portfolio/data/factories.py` |
| New environment | `.env` only; no code change |
| New browser in CI | matrix entry in `.github/workflows/ci.yml` |
| New layer (e.g. database) | new fixture module under `tests/` + `src/qa_portfolio/<layer>/` |

## Deliberate scope boundaries

Visual regression, performance budgets, security scanning and AI-assisted
generation are **not** here. They belong to `advanced-playwright-labs`,
`enterprise-qa-portfolio` and `playwright-ai-mcp-agent`, so this repository
stays a focused, fast reference for layered functional automation in Python.
