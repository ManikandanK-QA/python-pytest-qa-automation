# Test strategy

## Approach

Risk-based, layered coverage over two stable public demo systems:

- **SauceDemo** (`https://www.saucedemo.com`) — UI: sign-in, catalogue, cart, checkout.
- **Restful Booker** (`https://restful-booker.herokuapp.com`) — REST: token auth, CRUD, negative paths.

Both are documented, credential-free demo targets, so the repository is
clone-and-run while still exercising real authentication, state and validation.

## Coverage matrix

| Layer | Area | Scenarios | Markers |
| --- | --- | --- | --- |
| UI | Authentication | valid sign-in; locked-out user; wrong password; missing username; missing password | `smoke`, `ui` |
| UI | Catalogue | six products listed; ascending price sort; add/remove with badge sync | `smoke`, `ui` |
| UI | Cart | contents; removal updates count; continue shopping | `ui` |
| UI | Checkout | end-to-end purchase; mandatory postal code | `smoke`, `ui` |
| API | Auth | token issued; invalid credentials rejected (HTTP 200 + reason quirk) | `smoke`, `api` |
| API | Booking CRUD | create + read; name filter; full update; partial update; delete then 404 | `smoke`, `api` |
| API | Negative | unknown id → 404; write without token → 403; invalid payload → 500 | `api` |

24 tests in total: 13 UI (13 per browser if the matrix is expanded) and 11 API.

## Markers

| Marker | Intent | Command |
| --- | --- | --- |
| `smoke` | pre-merge confidence, under a minute | `pytest -m smoke` |
| `regression` | full functional sweep | `pytest -m regression` |
| `ui` | browser-driven only | `pytest -m ui` |
| `api` | REST only, no browser launched | `pytest -m api` |

`--strict-markers` is enabled, so a typo in a marker fails collection instead of
silently selecting nothing.

## Test data

- Static identities and expected strings live in `src/qa_portfolio/data/`; the
  negative login matrix is one parameterised array.
- API payloads come from `build_booking()` (Faker) with explicit overrides only
  where the assertion depends on a value. No shared mutable fixtures.
- Every API test owns its records: the factory deletes them in teardown.

## Determinism rules

1. No `wait_for_timeout`; Playwright web-first assertions and actionability
   checks only. Setup waits use `wait_for_url` / `wait_for(state=...)`.
2. No assertions inside page objects. A failure points at the spec line.
3. No cross-test ordering; every test is parallel-safe.
4. No hardcoded URLs in specs; targets come from validated settings.
5. No retries. A test that only passes on retry is a defect, not a pass.
6. Warnings are errors, except the single documented pytest-playwright
   deprecation in `pyproject.toml`.

## Browser coverage

The suite defaults to Chromium locally. The same specs run unchanged on Firefox
and WebKit:

```bash
pytest -m ui --browser firefox
pytest -m ui --browser webkit
```

CI runs the UI matrix across all three engines on Linux.

## Explicit non-goals

- Load, stress and soak testing — `enterprise-qa-portfolio` (k6).
- Visual comparison, network mocking, security scans — `advanced-playwright-labs`.
- AI-assisted scenario generation and failure triage — `playwright-ai-mcp-agent`.
- Manual and exploratory charters — documented outside code.

## Exit criteria for a change

- `ruff format --check .`, `ruff check .` and `mypy` pass.
- `pytest -m "ui or api"` passes locally.
- New behaviour has at least one happy path and one negative or boundary case.
- No new sleeps, no new hardcoded environment values, no assertion in a page
  object.
