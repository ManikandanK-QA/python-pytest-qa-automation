# CI/CD

## Pipeline

`.github/workflows/ci.yml` runs on every push and pull request to `main`, on a
nightly schedule, and on manual dispatch.

```
quality (ruff format --check, ruff check, mypy)
   ├─ ui: chromium ─┐
   ├─ ui: firefox   ┼─ publish (main only) → merged Allure report → gh-pages
   ├─ ui: webkit    ┤
   └─ api           ┘
```

Design points:

- **Quality gate first.** The browser matrix does not start when formatting,
  linting or typing fails.
- **Layer isolation.** The API job installs no browser at all: REST tests never
  launch one, so a UI regression cannot mask an API result.
- **One browser per job.** `python -m playwright install --with-deps <browser>`
  downloads only what that job needs.
- **Least privilege.** Workflow default is `contents: read`; only the publish
  job requests `contents: write`.
- **Concurrency.** Superseded runs on the same ref are cancelled.
- **Nightly run.** Scheduled tests catch drift in the third-party demo targets
  before a human notices.

## Parallelism inside a job

Every test job runs `pytest -n auto`. Fixtures are worker-local:

- one `storageState` file per worker (`PYTEST_XDIST_WORKER` in the filename);
- one HTTP client, and therefore one auth token, per worker;
- each API test deletes what it created, so no cross-worker interference.

## Artifacts

| Artifact | Contents | Retention |
| --- | --- | --- |
| `allure-<job>` | raw Allure results | 7 days |
| `junit-<job>` | JUnit XML | 7 days |
| `test-results-<job>` | Playwright traces, screenshots (failures only) | 7 days |

## Publishing the Allure report

On `main`, the publish job downloads every `allure-*` artifact, generates one
combined report and pushes it to the `gh-pages` branch.

Setup on GitHub (already applied for this repository):

1. **Settings → Pages → Deploy from a branch**
2. Branch: `gh-pages`, folder `/ (root)`
3. Report URL: `https://<user>.github.io/<repo>/`

The first successful run creates the branch. Later runs keep the trend history.

## Local parity

```bash
ruff format --check .     # same formatter gate as CI
ruff check .
mypy
pytest -m api             # API job, no browser needed
pytest -m ui              # UI job on the default browser
pytest -n auto            # full suite, parallel
```

`CI=true` is set by GitHub Actions. It is not used to change behaviour in this
project: the same command runs locally and in CI, so a green local run means
something.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Executable doesn't exist` | browser not installed | `python -m playwright install chromium` |
| `ModuleNotFoundError: qa_portfolio` | package not installed | `pip install -e ".[dev]"` |
| UI tests redirect to the sign-in page | stale or missing `.auth` file | delete `.auth/`, rerun |
| `AssertionError` in `_pytest/fixtures.py` | a warning was promoted to an error during fixture setup, masking the real cause | run with `-W default` to see the original warning |
| API 403 on write | token missing or expired | re-authenticate; the token is cached per `BookingApi` instance |
| Allure publish fails | Pages not configured for `gh-pages` | enable Pages as above |
| Flaky failure only in CI | different viewport or timing | reproduce with `CI=true pytest -m ui`, inspect the trace in `test-results/` |
