# Releasing, pull requests and reviews

Every change to the app or its data goes through a pull request (PR). That gives each change its own page with what changed, why, and when, so the closed PR list doubles as a record of the work on the app. The scheduled data jobs are the exception: they push routine updates straight to `main` (see [automation.md](automation.md)).

## The usual flow

1. **Make the change on a branch**, not on `main`. On GitHub's website, editing a file (pencil icon) and choosing **Create a new branch for this commit and start a pull request** does this for you. From a laptop, `./scripts/sync-release.sh` does it for a downloaded release zip (below).
2. **Open the pull request.** The **Build and deploy** check runs automatically: it checks the season data and builds the site, without publishing. A red cross means something would break; the **Details** link and the **Files changed** tab show which file and line.
3. **Merge it.** Maintainers can merge their own PRs straight away using their admin bypass (tick **Merge without waiting for requirements to be met**). Anyone else's PR needs approval from a member of the maintainers team first. Use **Create a merge commit** so each PR stays visible as one unit in the history.
4. **It goes live** a minute or two later: merging is a push to `main`, which runs **Build and deploy** again, this time publishing. A new app version is tagged automatically (`v2.17.0` and so on).

### Labels and milestones

To see where the effort goes, give each PR a label: `feature`, `fix`, `data` (programme, extras, courses) or `docs`. A milestone per season (for example "2027 season") groups the work for that year. **Insights → Pulse** summarises a week's or month's activity.

## Releasing from a zip

A release built outside the repo arrives as `bsc-sailing-app.zip`: the changed files at their repo paths (`app/index.html`, `data/extras-2026.csv` and so on), plus a `release-manifest.json`:

```json
{ "version": "2.17.0", "base_version": "2.16.6",
  "base_files":  { "app/index.html": "<git blob hash it was built from>", "app/new-file.html": null },
  "known_files": { "app/index.html": ["<an earlier release's hash>"] } }
```

`version` must match `CONFIG.version` in `app/index.html`, `VERSION` in `app/sw.js`, and the newest heading in `CHANGELOG.md` (bump all three, and `CONFIG.released`). `base_files` records each file as it was when the release was built (`git hash-object <file>`), or `null` for a new file; `known_files` lists other copies that are safe to replace, such as an earlier release's. A zip without `app/index.html` is a partial update (data or docs only) and gets no version.

To apply one, download it and run `./scripts/sync-release.sh` from the repo, on `main`. It:

1. finds the newest `bsc-sailing-app*.zip` in `~/Downloads` (or takes a path);
2. checks the version numbers inside agree, and refuses a zip older than the repo unless you insist (and a zip built before the repo moved the app into `app/`);
3. switches to the zip's copy of `sync-release.sh` first, if it has a newer one;
4. fast-forwards if GitHub is ahead (the scheduled data jobs push there daily);
5. warns before overwriting any file changed on GitHub since the release was built (files the scheduled jobs own are exempt), asking even with `-y`;
6. puts the files on a new branch (`release/v2.17.0`, or `update/<date-time>` for a partial update), commits and pushes it, and opens the pull request;
7. offers to merge it straight away with your admin bypass, then waits for the live site to show the new version;
8. moves the zip to `~/Downloads/bsc-sailing-app-applied/`, so the next download keeps the plain name.

Opening and merging the PR from the script needs the GitHub CLI, signed in: `brew install gh`, then `gh auth login`. Without it, the script prints a link to open the PR in your browser instead. Add `-y` to skip the routine questions.

## Rolling back

Open the merged PR on GitHub and click **Revert**. That opens a new PR undoing it; merge that, and the previous version is live again a minute or two later. Every version is also tagged, so `git diff v2.16.6 v2.17.0` shows exactly what a release changed.

## Branch ruleset and code owners

`main` is protected by a branch ruleset, and `.github/CODEOWNERS` names the `@bsc-sailing/maintainers` team as reviewers for every file. To set it up on a repo (or check it's still in place):

1. **Repo → Settings → Rulesets → New branch ruleset.** Target `main`.
2. Turn on **Require a pull request before merging**, set **Required approvals: 1**, and turn on **Require review from Code Owners**.
3. In **Bypass list**, add **Organization admin** (and **Repository admin**) with **Always allow**. Leave **"Do not allow bypassing the above settings"** off.

Step 3 is what lets a maintainer merge their own PRs without waiting for anyone: GitHub never lets anyone approve their own pull request, code owner or not, so without the bypass the only people allowed to approve would be unable to approve their own work. It also lets the scheduled data jobs push as a maintainer (see [automation.md](automation.md)) — which is why the bypass must be **Always allow**, not **For pull requests only**. Anyone who isn't a bypass-eligible admin has no workaround: their PRs always need a maintainer's approval.

## Publishing settings

The site is published by `.github/workflows/deploy.yml`, which needs **Settings → Pages → Build and deployment → Source: GitHub Actions**. `scripts/build-site.py` assembles it from `app/`, `app/assets/`, `data/` and `templates/`, publishing every file side by side at the same addresses as before the repo was split into folders; see the README's "Repo layout".

To check a build locally: `python3 scripts/check-data.py && python3 scripts/build-site.py`, then `cd _site && python3 -m http.server` and open `http://localhost:8000/`.
