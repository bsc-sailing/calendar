#!/usr/bin/env bash
# sync-release.sh — apply a downloaded bsc-sailing-app.zip to this repo as a
# pull request, optionally merge it, and confirm it's live.
#
# The release's version comes from release-manifest.json in the zip (and is
# checked against index.html, sw.js and CHANGELOG.md). A zip older than what's
# in the repo is refused unless you insist. If the zip carries a newer copy of
# this script, it switches to that copy and carries on. Once applied, the zip
# is moved to ~/Downloads/bsc-sailing-app-applied/, so the next download keeps
# the plain name.
#
# The zip's files go onto a new branch (release/vX.Y.Z), which is pushed and
# opened as a pull request, so every release has its own PR in the history.
# With the GitHub CLI (gh) installed and signed in, it opens the PR for you
# and offers to merge it straight away using your admin bypass; without gh,
# it prints the link to open the PR in your browser. Merging publishes the
# site (.github/workflows/deploy.yml), which also tags the version.
#
# Usage:
#   ./scripts/sync-release.sh                 # picks the newest zip in ~/Downloads
#   ./scripts/sync-release.sh path/to/some.zip # use a specific zip
#   ./scripts/sync-release.sh -y               # don't pause for routine confirmations
#
# If GitHub has commits this checkout doesn't (usually the scheduled data jobs),
# it fast-forwards first. If the zip carries a release-manifest.json, it then
# checks whether any file the zip replaces has changed on GitHub since the
# release was built, so nothing gets silently overwritten. Those warnings
# always need a typed "y", even with -y.
#
# Expects to be run from anywhere inside the repo. Safe to re-run: it stops
# rather than guesses whenever something looks wrong.

set -euo pipefail

# ---- settings you might want to change if you reuse this for another repo
EXPECTED_REMOTE="github.com/bsc-sailing/calendar"
EXPECTED_EMAIL_SUFFIX="@users.noreply.github.com"
DOWNLOADS_DIR="${DOWNLOADS_DIR:-$HOME/Downloads}"
ZIP_GLOB="bsc-sailing-app*.zip"
SELF_PATH="scripts/sync-release.sh"
# Files the scheduled jobs rewrite on their own: a release may replace them,
# and the next scheduled run regenerates them, so they never count as conflicts.
BOT_FILES=("data/events.json" "data/tides.json" "data/tides-official.csv")
INDEX="app/index.html"
SW="app/sw.js"

# ---- helpers
c_bold=$'\033[1m'; c_grn=$'\033[32m'; c_red=$'\033[31m'; c_yel=$'\033[33m'; c_off=$'\033[0m'
info()  { printf '%s\n' "$*"; }
ok()    { printf '%s%s%s\n' "$c_grn" "$*" "$c_off"; }
warn()  { printf '%s%s%s\n' "$c_yel" "$*" "$c_off"; }
die()   { printf '%s%s%s\n' "$c_red" "$*" "$c_off" >&2; exit 1; }
confirm() {
  $ASSUME_YES && return 0
  read -r -p "$1 [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}
confirm_always() {   # ignores -y: for anything that could lose someone else's work
  read -r -p "$1 [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}

# Once a zip from Downloads has been applied, move it out of the way so the
# next download keeps the plain name (no "bsc-sailing-app (1).zip").
APPLIED_DIR="$DOWNLOADS_DIR/bsc-sailing-app-applied"
archive_zip() {
  [[ -n "${ZIP_FROM_DOWNLOADS:-}" && -f "${ZIP_PATH:-}" ]] || return 0
  mkdir -p "$APPLIED_DIR"
  local name="bsc-sailing-app-${NEW_VERSION:-partial-$(date +%Y%m%d-%H%M%S)}.zip"
  mv -f "$ZIP_PATH" "$APPLIED_DIR/$name" && info "Moved the zip to $APPLIED_DIR/$name"
  local left; left="$(ls "$DOWNLOADS_DIR"/$ZIP_GLOB 2>/dev/null | wc -l | tr -d ' ')"
  [[ "$left" -gt 0 ]] && warn "$left other $ZIP_GLOB file(s) still in $DOWNLOADS_DIR, probably old downloads. Delete them so the next run can't pick one up by mistake."
  return 0
}

ASSUME_YES=false
ZIP_ARG=""
for arg in "$@"; do
  case "$arg" in
    -y|--yes) ASSUME_YES=true ;;
    *) ZIP_ARG="$arg" ;;
  esac
done

# ---- find the repo root and sanity-check it
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Not inside a git repo. cd into the calendar folder first."
cd "$REPO_ROOT"

REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
[[ "$REMOTE_URL" == *"$EXPECTED_REMOTE"* ]] || die "origin is '$REMOTE_URL', not $EXPECTED_REMOTE. Wrong folder?"

GIT_EMAIL="$(git config user.email || true)"
[[ "$GIT_EMAIL" == *"$EXPECTED_EMAIL_SUFFIX" ]] || die "git user.email is '$GIT_EMAIL', expected something ending $EXPECTED_EMAIL_SUFFIX. Set it for this repo with: git config user.email <your GitHub noreply address>"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$CURRENT_BRANCH" == "main" ]] || die "On branch '$CURRENT_BRANCH', not main. Switch first: git checkout main"

# ---- find the zip
if [[ -n "$ZIP_ARG" ]]; then
  ZIP_PATH="$ZIP_ARG"
  [[ -f "$ZIP_PATH" ]] || die "No such file: $ZIP_PATH"
else
  ZIP_PATH="$(ls -t "$DOWNLOADS_DIR"/$ZIP_GLOB 2>/dev/null | head -n1 || true)"
  [[ -n "$ZIP_PATH" ]] || die "No $ZIP_GLOB found in $DOWNLOADS_DIR. Pass a path: ./scripts/sync-release.sh path/to/zip"
fi
info "Zip:    $ZIP_PATH"
ZIP_FROM_DOWNLOADS=""
[[ -z "$ZIP_ARG" || -n "${SYNC_ZIP_FROM_DOWNLOADS:-}" ]] && ZIP_FROM_DOWNLOADS=1

# warn if there's more than one candidate zip and we picked by recency — this is
# exactly the "bsc-sailing-app (1).zip" mix-up that's bitten before
if [[ -z "$ZIP_ARG" ]]; then
  CANDIDATES="$(ls -t "$DOWNLOADS_DIR"/$ZIP_GLOB 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$CANDIDATES" -gt 1 ]]; then
    warn "$CANDIDATES matching zips in $DOWNLOADS_DIR — using the most recently downloaded one:"
    ls -t "$DOWNLOADS_DIR"/$ZIP_GLOB | sed 's/^/  /'
    echo
  fi
fi

# ---- unzip to a scratch dir
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
unzip -q "$ZIP_PATH" -d "$WORK_DIR"
MANIFEST="$WORK_DIR/release-manifest.json"

# ---- versions. A full release (one with index.html) gets a version and a tag;
# a partial one (docs or a single file) doesn't.
read_index_version() { grep -o 'version: "[0-9][0-9.]*"' "$1" 2>/dev/null | head -n1 | grep -o '[0-9][0-9.]*' || true; }
ver_cmp() {   # prints -1, 0 or 1
  python3 -c 'import sys; a,b=[[int(x) for x in v.split(".")] for v in sys.argv[1:3]]; print((a>b)-(a<b))' "$1" "$2"
}

PARTIAL=false
NEW_VERSION=""
if [[ -f "$MANIFEST" ]]; then
  NEW_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("version",""))' "$MANIFEST")"
fi
if [[ -f "$WORK_DIR/index.html" ]]; then
  die "This zip has index.html at the top level, so it was built before the repo moved the app into app/. Ask for a zip built for the current layout."
fi
if [[ -f "$WORK_DIR/$INDEX" ]]; then
  IDX_VERSION="$(read_index_version "$WORK_DIR/$INDEX")"
  [[ -n "$IDX_VERSION" ]] || die "$INDEX is in the zip but has no readable version number."
  [[ -z "$NEW_VERSION" ]] && NEW_VERSION="$IDX_VERSION"
  # every place the version appears must agree, or the release was built wrong
  MISMATCH=""
  [[ "$IDX_VERSION" == "$NEW_VERSION" ]] || MISMATCH+=" index.html says $IDX_VERSION;"
  if [[ -f "$WORK_DIR/$SW" ]]; then
    SW_VERSION="$(grep -o 'VERSION = "[0-9][0-9.]*"' "$WORK_DIR/$SW" | head -n1 | grep -o '[0-9][0-9.]*' || true)"
    [[ "$SW_VERSION" == "$NEW_VERSION" ]] || MISMATCH+=" sw.js says ${SW_VERSION:-nothing};"
  fi
  if [[ -f "$WORK_DIR/CHANGELOG.md" ]]; then
    CL_VERSION="$(grep -m1 -o '^## [0-9][0-9.]*' "$WORK_DIR/CHANGELOG.md" | grep -o '[0-9][0-9.]*' || true)"
    [[ "$CL_VERSION" == "$NEW_VERSION" ]] || MISMATCH+=" CHANGELOG.md's newest entry is ${CL_VERSION:-missing};"
  fi
  [[ -z "$MISMATCH" ]] || die "This zip's version numbers don't agree (release $NEW_VERSION):$MISMATCH Ask for a corrected zip."
else
  PARTIAL=true
fi

if $PARTIAL; then
  warn "No $INDEX in this zip, so it's a partial update (docs or single files, no version tag)."
  info "Files in this zip:"
  ( cd "$WORK_DIR" && find . -type f ! -name release-manifest.json ) | sed 's/^/  /'
fi

# ---- if the zip has a newer copy of this script, switch to it now, so the
# rest of the run uses the new rules. It's committed with everything else.
PRE_VERSION="$(read_index_version "$REPO_ROOT/$INDEX")"
NOT_OLDER=true
if ! $PARTIAL && [[ -n "$PRE_VERSION" ]] && [[ "$(ver_cmp "$NEW_VERSION" "$PRE_VERSION")" == "-1" ]]; then NOT_OLDER=false; fi
if $NOT_OLDER && [[ -f "$WORK_DIR/$SELF_PATH" ]] && ! cmp -s "$WORK_DIR/$SELF_PATH" "$REPO_ROOT/$SELF_PATH" && [[ -z "${SYNC_REEXEC:-}" ]]; then
  [[ -z "$(git status --porcelain -- "$SELF_PATH")" ]] || die "$SELF_PATH has local changes that don't match this zip. Run 'git status' and deal with that first."
  info "This zip has an updated $SELF_PATH. Switching to it."
  cp "$WORK_DIR/$SELF_PATH" "$REPO_ROOT/$SELF_PATH"; chmod +x "$REPO_ROOT/$SELF_PATH"
  rm -rf "$WORK_DIR"
  REEXEC_ARGS=()
  $ASSUME_YES && REEXEC_ARGS+=("-y")
  SYNC_REEXEC=1 SYNC_ZIP_FROM_DOWNLOADS="$([[ -z "$ZIP_ARG" ]] && echo 1 || true)" exec "$REPO_ROOT/$SELF_PATH" "${REEXEC_ARGS[@]+"${REEXEC_ARGS[@]}"}" "$ZIP_PATH"
fi

# Clean working tree, with one exception: this script itself may have been
# replaced by hand from the zip (the way a new version of it arrives). That's
# checked against the zip's copy further down.
DIRTY="$(git status --porcelain | grep -v " $SELF_PATH\$" || true)"
[[ -z "$DIRTY" ]] || die "Working tree isn't clean. Run 'git status' and deal with that before syncing a release."
SELF_DIRTY=false
[[ -n "$(git status --porcelain -- "$SELF_PATH")" ]] && SELF_DIRTY=true

git fetch origin --quiet || die "git fetch failed — check your connection and that your token hasn't expired."
REMOTE_REV="$(git rev-parse @{u} 2>/dev/null)" || die "main has no upstream branch. Run: git branch --set-upstream-to=origin/main"
AHEAD="$(git rev-list --count @{u}..@)"; BEHIND="$(git rev-list --count @..@{u})"
if [[ "$AHEAD" -gt 0 ]]; then
  die "This checkout has $AHEAD commit(s) that aren't on GitHub (and is $BEHIND behind). Sort that out by hand first: git pull --rebase, then git push."
fi
if [[ "$BEHIND" -gt 0 ]]; then
  info "GitHub has $BEHIND commit(s) this checkout doesn't:"
  git log --oneline --no-decorate @..@{u} | sed 's/^/  /' | head -n 20
  [[ "$BEHIND" -gt 20 ]] && info "  ... and $((BEHIND - 20)) more"
  confirm "Fast-forward to match GitHub?" || die "Stopped. Run 'git pull' yourself, then re-run this."
  git merge --ff-only --quiet @{u} || die "Fast-forward failed. Run 'git pull' and look at what it says."
  ok "Up to date with origin/main."
fi

# ---- compare with what's in the repo now (after catching up with GitHub)
CURRENT_VERSION="$(read_index_version "$REPO_ROOT/$INDEX")"
if ! $PARTIAL; then
  echo
  info "${c_bold}In this checkout: ${CURRENT_VERSION:-none}${c_off}"
  info "${c_bold}Zip contains:     $NEW_VERSION${c_off}"
  echo
  if [[ -n "$CURRENT_VERSION" ]]; then
    case "$(ver_cmp "$NEW_VERSION" "$CURRENT_VERSION")" in
      -1) warn "This zip is OLDER than what's already in the repo. Applying it would roll the app back."
          info "(To roll back on purpose, the backup tags are safer: git tag -l 'backup-*')"
          confirm_always "Roll back to $NEW_VERSION anyway?" || { info "Stopped. Nothing was changed."; exit 0; } ;;
       0) warn "That's the same version already in the repo. Nothing to do, unless you're re-applying it deliberately."
          confirm "Continue anyway?" || { info "Stopped."; exit 0; } ;;
    esac
  fi
fi

info "Repo:   $REPO_ROOT"
info "Remote: $REMOTE_URL"
info "Email:  $GIT_EMAIL"
echo

# A hand-replaced copy of this script must be exactly the zip's copy
if $SELF_DIRTY; then
  if [[ -f "$WORK_DIR/$SELF_PATH" ]] && cmp -s "$WORK_DIR/$SELF_PATH" "$REPO_ROOT/$SELF_PATH"; then
    info "Running the new $SELF_PATH from this zip."
  else
    die "$SELF_PATH has local changes that don't match this zip. Run 'git status' and deal with that first."
  fi
fi

# ---- has anything this zip replaces changed on GitHub since the release was built?
MANIFEST="$WORK_DIR/release-manifest.json"
if [[ -f "$MANIFEST" ]]; then
  BASE_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("base_version",""))' "$MANIFEST")"
  CONFLICTS="$(python3 - "$MANIFEST" "$WORK_DIR" "${BOT_FILES[@]}" <<'PY'
import json, os, subprocess, sys
manifest, work, bots = sys.argv[1], sys.argv[2], set(sys.argv[3:])
m = json.load(open(manifest))
base = m.get("base_files", {})
known = m.get("known_files", {})   # earlier releases' copies: safe to replace too
def blob(path):
    return subprocess.run(["git", "hash-object", path], capture_output=True, text=True).stdout.strip() if os.path.isfile(path) else None
for path, base_hash in sorted(base.items()):
    if path in bots:
        continue
    now = blob(path)
    if now == base_hash or now in known.get(path, []):
        continue                       # untouched since the release was built, or an earlier release's copy
    if now is not None and now == blob(os.path.join(work, path)):
        continue                       # already identical to the release
    if base_hash is None:
        print(f"{path}\tcreated on GitHub, but this release adds its own")
    elif now is None:
        print(f"{path}\tdeleted on GitHub, but this release puts it back")
    else:
        print(f"{path}\tchanged on GitHub since this release was built")
PY
)"
  if [[ -n "$CONFLICTS" ]]; then
    echo
    warn "These files have changed on GitHub since this release was built from v${BASE_VERSION:-?}. Applying it would overwrite those changes:"
    while IFS=$'\t' read -r f why; do
      info "  ${c_bold}$f${c_off}: $why"
      if [[ -n "$BASE_VERSION" ]] && git rev-parse -q --verify "v$BASE_VERSION" >/dev/null; then
        git log --oneline --no-decorate "v$BASE_VERSION"..HEAD -- "$f" | sed 's/^/      /' | head -n 5
      fi
    done <<< "$CONFLICTS"
    echo
    info "To see exactly what changed:  git diff v${BASE_VERSION:-<tag>} -- <file>"
    info "If those changes still matter, stop here and get a release that includes them."
    confirm_always "Overwrite them anyway?" || { info "Stopped. Nothing was changed."; exit 0; }
  else
    ok "Nothing this release replaces has changed on GitHub since it was built."
  fi
fi

if ! $PARTIAL; then
  confirm "Apply v$NEW_VERSION from this zip?" || { info "Stopped."; exit 0; }
else
  confirm "Apply this partial update (no version tag will be created)?" || { info "Stopped."; exit 0; }
fi

# ---- the release goes on its own branch, which becomes the pull request
if $PARTIAL; then BRANCH="update/$(date +%Y%m%d-%H%M%S)"; else BRANCH="release/v$NEW_VERSION"; fi
if git rev-parse -q --verify "refs/heads/$BRANCH" >/dev/null || git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  die "Branch $BRANCH already exists (here or on GitHub), probably from an earlier run. Finish or close that PR first, or delete the branch: git branch -D $BRANCH; git push origin --delete $BRANCH"
fi
git checkout -q -b "$BRANCH"
back_to_main() { git checkout -q main; }
abandon_branch() { git reset -q --hard; back_to_main; git branch -q -D "$BRANCH"; }

# ---- copy the new files in (does not delete files that aren't in the zip —
# if a release is meant to remove a file, do that with a manual git rm)
info "Copying files into $REPO_ROOT ..."
( cd "$WORK_DIR" && find . -type f ! -name release-manifest.json ) | while read -r f; do
  mkdir -p "$REPO_ROOT/$(dirname "$f")"
  cp "$WORK_DIR/$f" "$REPO_ROOT/$f"
done

git add -A
echo
info "${c_bold}Changes to commit:${c_off}"
git status --short
echo

if [[ -z "$(git status --porcelain)" ]]; then
  warn "Nothing changed after copying — the working tree already matched this zip."
  abandon_branch
  archive_zip
  exit 0
fi

if $PARTIAL; then
  confirm "Commit it and open a pull request?" || { abandon_branch; info "Stopped. Nothing was changed."; exit 0; }
else
  confirm "Commit v$NEW_VERSION and open a pull request?" || { abandon_branch; info "Stopped. Nothing was changed."; exit 0; }
fi

# ---- commit message: a version header for a full release (with notes pulled
# from CHANGELOG.md's newest entry, if present), or a plain summary of what
# changed for a partial one — there's no version to head it with
if $PARTIAL; then
  FILES_CHANGED="$(git diff --cached --name-only | tr '\n' ' ')"
  COMMIT_MSG="Update: $FILES_CHANGED"
else
  COMMIT_MSG="v$NEW_VERSION"
  if [[ -f "$REPO_ROOT/CHANGELOG.md" ]]; then
    NOTES="$(awk '/^## /{n++} n==1 && !/^## /' "$REPO_ROOT/CHANGELOG.md" | sed '/^\s*$/d' | head -n 6)"
    [[ -n "$NOTES" ]] && COMMIT_MSG="$(printf 'v%s\n\n%s' "$NEW_VERSION" "$NOTES")"
  fi
fi

git commit -q -m "$COMMIT_MSG"
git push -q -u origin "$BRANCH"
ok "Pushed branch $BRANCH."

if $PARTIAL; then PR_TITLE="$(printf '%s' "$COMMIT_MSG" | head -n1)"; else PR_TITLE="v$NEW_VERSION"; fi
PR_BODY="$(printf '%s\n\n---\nApplied from %s by scripts/sync-release.sh.' "$(printf '%s' "$COMMIT_MSG" | tail -n +3)" "$(basename "$ZIP_PATH")")"
COMPARE_URL="https://$EXPECTED_REMOTE/compare/main...$BRANCH?expand=1"

if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1; then
  back_to_main
  archive_zip
  warn "The GitHub CLI (gh) isn't installed or signed in, so open the pull request in your browser:"
  info "  $COMPARE_URL"
  info "Merging it publishes the site and tags the version."
  exit 0
fi

PR_URL="$(gh pr create --base main --head "$BRANCH" --title "$PR_TITLE" --body "$PR_BODY")"
ok "Opened $PR_URL"
back_to_main
archive_zip

if ! confirm "Merge it now (uses your admin bypass)?"; then
  info "Left open for review. Merging it publishes the site and tags the version."
  exit 0
fi
gh pr merge "$PR_URL" --merge --admin --delete-branch
git pull -q --ff-only
ok "Merged."

if $PARTIAL; then exit 0; fi
echo

# ---- poll the live site until the new version shows, rather than guessing how long to wait
PAGES_URL="https://bsc-sailing.github.io/calendar/"
info "Checking $PAGES_URL for v$NEW_VERSION (up to 4 minutes) ..."
for i in $(seq 1 24); do
  LIVE_VERSION="$(curl -fsSL "$PAGES_URL" 2>/dev/null | grep -o 'version: "[0-9][0-9.]*"' | head -n1 | grep -o '[0-9][0-9.]*' || true)"
  if [[ "$LIVE_VERSION" == "$NEW_VERSION" ]]; then
    ok "Live: v$LIVE_VERSION"
    exit 0
  fi
  sleep 10
done
warn "Still showing v${LIVE_VERSION:-unknown} after 4 minutes. Check the repo's Actions tab ("Build and deploy") for a failed run."
