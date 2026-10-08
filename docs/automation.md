# Scheduled jobs and automation

Four GitHub Actions workflows keep data up to date without anyone running anything, and a fifth publishes the site. This page covers what each one touches, how they're allowed to push, and what to look at if one stops.

| Workflow | When | What it changes |
| --- | --- | --- |
| `deploy.yml` — Build and deploy | Every push to `main`; check-only on every pull request | Publishes the site; tags new versions. See [releasing.md](releasing.md). |
| `update-events.yml` — Update club events | Daily, 06:17 UTC | `data/events.json` only |
| `update-tides.yml` — Update tide reference | Weekly, Sunday 06:43 UTC | `data/tides.json` only |
| `check-official-tides.yml` — Check published tides | Daily, 04:20 UTC | `data/tides-official.csv` and `data/tides.json` |
| `extra-date.yml` — Extra date request | When an **Add an extra date** issue is opened, edited or labelled `approved` | Opens a pull request adding a row to `data/extras-YEAR.csv` |

Each data job only commits when the *data* actually changed (the files' own `generated` timestamps are ignored when comparing), so a quiet week in the Actions history is normal, not a sign anything's wrong. Their commits are pushes to `main`, so each one also triggers a deploy.

You can run any of them early from **Actions → (workflow name) → Run workflow**.

## RELEASE_TOKEN: how the data jobs push to `main`

The data jobs push straight to `main`, with no pull request, authenticating as a real account (`jfairhead`) via a repository secret called `RELEASE_TOKEN`, rather than the default `github-actions[bot]` identity. This repo's ruleset bypass list has no entry for GitHub Actions itself — only for roles, teams and installed Apps — so a plain Actions-identity push would be blocked by the same "require a pull request" rule as anyone else's. Authenticating as a `maintainers`-team member sidesteps that: the push is allowed for the same reason any of that person's own pushes are.

This is safe to grant because each job can only ever touch its own generated files, sourced from fixed URLs, and every field from them is shown in the app as plain text — never as HTML — so nothing fetched can affect how the app behaves. It does **not** extend to changes to the workflow files themselves: `.github/workflows/*.yml` needs a token with the `workflow` permission to push, and goes through normal PR review — so what the jobs are *allowed to do* is always reviewed, even though their routine output isn't.

Two consequences worth knowing:

- **Keep the token owner's ruleset bypass set to "Always allow"**, not "For pull requests only". The second option would stop these direct pushes and the jobs would start failing.
- **Pushes made with this token trigger other workflows**, which is why the data jobs' commits reach the live site. (Pushes made with the built-in Actions token don't, by GitHub's design.)

**Setup:** create a fine-grained personal access token scoped to only this repo, **Contents: Read and write** (nothing else needed), under an account on the `maintainers` team. Add it at **Settings → Secrets and variables → Actions → New repository secret**, named `RELEASE_TOKEN`. Tokens expire: when the jobs start failing with an authentication error, make a new one and replace the secret.

## Club events

The club website doesn't let other sites read its event feed directly from a visitor's browser (no CORS headers), so the app can't fetch it live the way it does the weather forecast. Instead, `update-events.yml` fetches the club's public RSS feed (`https://blackwatersailingclub.org.uk/events/RSS`) from GitHub's servers once a day and converts it with `scripts/update-events.py`.

- A feed that returns zero events (an outage, or the club changing its page) is treated as a failure, not "no events": the existing file is left alone and the run logs a warning.
- Only upcoming events show in the app; past ones drop off on their own.
- **If it stops finding anything:** the club's feed URL or structure has probably changed. Check the RSS address still returns XML in the same shape, and adjust `scripts/update-events.py` if not.

## Tide reference

`data/tides.json` is a rolling 24-month list of high waters, one per day, kept separate from the hand-prepared programme files so nothing automated ever writes to those. The method and its accuracy are in `scripts/tide/TIDES.md`.

- **Why a rolling file:** a date has a sensible tide *before* that season's programme exists, and the fit improves as seasons accumulate — `generate-tide-reference.py` pools every `data/programme-*.csv`, not just the latest.
- **Real data always wins:** a date printed in a programme uses that exact value, so the app can never show two different numbers for the same date.
- **Worth glancing at each run:** the log prints an accuracy check (time and height error against the known points). A sudden jump usually means a newly added season's data looks unusual.

`check-official-tides.yml` reads the next 7 days from the club website's pontoon tide table every morning, records them in `data/tides-official.csv` alongside what the model had estimated, and refits. The coming week then shows the published times without the `≈`. Details, including the optional ADMIRALTY comparison, are in `scripts/tide/TIDES.md`, "Checking against published tide predictions". The two tide jobs share a concurrency group, so they never write `tides.json` at the same time.

## Extra-date requests

The **Add an extra date** issue form (`.github/ISSUE_TEMPLATE/extra-date.yml`) and `extra-date.yml` turn a request into a pull request. Nothing reaches the app without a maintainer's approval:

1. When the person asking has write access to this repo, the workflow checks the form straight away. Anyone else gets a reply saying a maintainer will review it, and nothing happens until a maintainer adds the `approved` label (only people with triage or write access can label).
2. If a field doesn't make sense (a date in the past, a start time that isn't `HH:MM`), it comments on the issue saying what to fix. Editing the issue re-checks it.
3. Otherwise it opens a pull request adding the row to `data/extras-YEAR.csv` (with a tide from `tides.json`), and renames the issue "Extra date: YYYY-MM-DD Name". The workflow recognises a request by the form's questions, so whatever title the requester types doesn't matter.
4. Merging the PR publishes it and closes the issue.

Every field is treated as untrusted text: checked against what it should look like, stripped of control characters, length-limited, read from the event file rather than pasted into a shell command, and shown in the app as plain text only.

The PR is opened by `github-actions[bot]`, so either code owner can approve it, including whoever asked. Because it's opened with the built-in token, the deploy workflow's check doesn't run on it automatically (GitHub's design, as above); the check runs when it's merged, and a bad row would stop the deploy rather than reach the site.

**One-off setup:** create an `approved` label (**Issues → Labels → New label**); turn on **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests** (it may also need allowing at org level); and make sure `.github/CODEOWNERS` lists the maintainers team, each member with write access.
