# Publishing the `datadough` package

The package is published by GitHub Actions (`.github/workflows/publish.yml`) with **trusted
publishing**: PyPI trusts this repository's workflow directly, so there's no API token to create, copy or
leak. The workflow is **off** until you set the repository variable in step 4.

You do steps 1–4 once. After that, every release is step 6.

## 1. Accounts

Create an account on both, and turn on two-factor authentication (both require it to publish):

- https://test.pypi.org/account/register/ (a separate test site with its own accounts)
- https://pypi.org/account/register/

## 2. Register the trusted publisher on TestPyPI

TestPyPI → your account → **Publishing** → **Add a new pending publisher** → **GitHub**:

| Field | Value |
|---|---|
| PyPI Project Name | `datadough` |
| Owner | `VedantParashar` |
| Repository name | `finance-analyzer` |
| Workflow name | `publish.yml` |
| Environment name | `testpypi` |

"Pending" means the project doesn't exist yet; the first upload creates it.

## 3. Register it on PyPI

Same form on https://pypi.org/manage/account/publishing/, with **Environment name** `pypi`.

## 4. Turn the workflow on

In this repository on GitHub:

1. **Settings → Environments → New environment** `testpypi`, then again for `pypi`. For `pypi`, tick
   **Required reviewers** and add yourself: every real release then waits for your click.
2. **Settings → Secrets and variables → Actions → Variables → New repository variable**:
   name `PYPI_PUBLISHING`, value `true`.

## 5. Try it on TestPyPI

**Actions → publish → Run workflow** (on `master`). It runs the tests, builds the package and uploads it
to TestPyPI. Then, in a new folder:

```bash
uv venv && uv pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ datadough
SEC_USER_AGENT="Your Name you@example.com" uv run python -c "import finance_analyzer as dd; print(dd.get_company('AAPL'))"
```

(`--extra-index-url` fetches the dependencies, like pandas, from the real PyPI.)

TestPyPI, like PyPI, never accepts the same version twice. To try again, raise the version in
`pyproject.toml` (e.g. `1.4.1`), run `uv lock`, and merge before running the workflow.

## 6. Publish a release to PyPI

1. Make sure `pyproject.toml`'s version is the one you're releasing and CHANGELOG.md has its date.
2. GitHub → **Releases → Draft a new release** → tag `v1.4.0` (the letter v plus the exact version) →
   **Publish release**.
3. The workflow checks the tag matches `pyproject.toml` (it stops if not), runs the tests, builds, and
   waits for your approval in the `pypi` environment. Approve it.
4. Check https://pypi.org/project/datadough/ and `pip install datadough`.

A version can't be changed or reused once it's on PyPI. If something's wrong, fix it and release the
next version; "yank" the broken one on PyPI if people shouldn't install it.

## To turn it off again

Delete the `PYPI_PUBLISHING` variable (or set it to anything but `true`).
