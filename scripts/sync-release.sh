#!/usr/bin/env bash
# sync-release.sh — apply a downloaded bsc-sailing-app.zip to this repo,
# back up the previous version, commit, push, tag, and confirm it's live.
#
# Usage:
#   ./scripts/sync-release.sh                 # picks the newest zip in ~/Downloads
#   ./scripts/sync-release.sh path/to/some.zip # use a specific zip
#   ./scripts/sync-release.sh -y               # don't pause for confirmation
#
# Expects to be run from anywhere inside the repo. Safe to re-run: it stops
# rather than guesses whenever something looks wrong.

set -euo pipefail

# ---- settings you might want to change if you reuse this for another repo
EXPECTED_REMOTE="github.com/bsc-sailing/calendar"
EXPECTED_EMAIL_SUFFIX="@users.noreply.github.com"
DOWNLOADS_DIR="${DOWNLOADS_DIR:-$HOME/Downloads}"
ZIP_GLOB="bsc-sailing-app*.zip"

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
[[ "$GIT_EMAIL" == *"$EXPECTED_EMAIL_SUFFIX" ]] || die "git user.email is '$GIT_EMAIL', expected something ending $EXPECTED_EMAIL_SUFFIX. Check .gitconfig-bsc is set up (see README)."

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$CURRENT_BRANCH" == "main" ]] || die "On branch '$CURRENT_BRANCH', not main. Switch first: git checkout main"

git fetch origin --quiet || die "git fetch failed — check your connection and that your token hasn't expired."
LOCAL_REV="$(git rev-parse @)"; REMOTE_REV="$(git rev-parse @{u} 2>/dev/null || echo "")"
[[ "$LOCAL_REV" == "$REMOTE_REV" ]] || die "Local main isn't in sync with origin/main. Run 'git pull' (or resolve conflicts) first."

[[ -z "$(git status --porcelain)" ]] || die "Working tree isn't clean. Run 'git status' and deal with that before syncing a release."

info "Repo:   $REPO_ROOT"
info "Remote: $REMOTE_URL"
info "Email:  $GIT_EMAIL"
echo

# ---- find the zip
if [[ -n "$ZIP_ARG" ]]; then
  ZIP_PATH="$ZIP_ARG"
  [[ -f "$ZIP_PATH" ]] || die "No such file: $ZIP_PATH"
else
  ZIP_PATH="$(ls -t "$DOWNLOADS_DIR"/$ZIP_GLOB 2>/dev/null | head -n1 || true)"
  [[ -n "$ZIP_PATH" ]] || die "No $ZIP_GLOB found in $DOWNLOADS_DIR. Pass a path: ./scripts/sync-release.sh path/to/zip"
fi
info "Zip:    $ZIP_PATH"

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

# ---- unzip to a scratch dir. index.html is how a full release's version
# gets read and tagged — if this zip doesn't have one (a docs-only or
# single-file fix, e.g. just a README), skip version handling entirely
# rather than refusing to apply the zip at all.
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
unzip -q "$ZIP_PATH" -d "$WORK_DIR"

PARTIAL=false
NEW_VERSION=""
if [[ -f "$WORK_DIR/index.html" ]]; then
  NEW_VERSION="$(grep -o 'version: "[0-9][0-9.]*"' "$WORK_DIR/index.html" | head -n1 | grep -o '[0-9][0-9.]*')"
  [[ -n "$NEW_VERSION" ]] || die "index.html is in the zip but has no readable version number."
else
  PARTIAL=true
  warn "No index.html in this zip — treating it as a partial update (docs/files only, no version tag)."
  info "Files in this zip:"
  ( cd "$WORK_DIR" && find . -type f ) | sed 's/^/  /'
fi

CURRENT_VERSION=""
if [[ -f "$REPO_ROOT/index.html" ]]; then
  CURRENT_VERSION="$(grep -o 'version: "[0-9][0-9.]*"' "$REPO_ROOT/index.html" | head -n1 | grep -o '[0-9][0-9.]*' || true)"
fi

if ! $PARTIAL; then
  echo
  info "${c_bold}Currently live (as far as this checkout goes): ${CURRENT_VERSION:-none}${c_off}"
  info "${c_bold}Zip contains:                                  $NEW_VERSION${c_off}"
  echo

  if [[ "$NEW_VERSION" == "$CURRENT_VERSION" ]]; then
    warn "That's the same version already in the repo. Nothing to do, unless you're re-applying it deliberately."
    confirm "Continue anyway?" || { info "Stopped."; exit 0; }
  fi

  confirm "Apply v$NEW_VERSION from this zip?" || { info "Stopped."; exit 0; }
else
  confirm "Apply this partial update (no version tag will be created)?" || { info "Stopped."; exit 0; }
fi

# ---- back up the current version as a tag, before changing anything —
# skipped for a partial update, since there's no new version to back up in
# front of (the existing v$CURRENT_VERSION tag already covers this state)
if ! $PARTIAL; then
  BACKUP_TAG="backup-before-v$NEW_VERSION"
  if git rev-parse "$BACKUP_TAG" >/dev/null 2>&1; then
    info "Tag $BACKUP_TAG already exists — skipping (probably a re-run)."
  else
    git tag -a "$BACKUP_TAG" -m "Live version before v$NEW_VERSION"
    git push origin "$BACKUP_TAG"
    ok "Pushed backup tag $BACKUP_TAG"
  fi
fi

# ---- copy the new files in (does not delete files that aren't in the zip —
# if a release is meant to remove a file, do that with a manual git rm)
info "Copying files into $REPO_ROOT ..."
( cd "$WORK_DIR" && find . -type f ) | while read -r f; do
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
  exit 0
fi

if $PARTIAL; then
  confirm "Commit and push this partial update?" || { info "Stopped. Changes are staged but not committed — 'git restore --staged .' to undo."; exit 0; }
else
  confirm "Commit and push v$NEW_VERSION?" || { info "Stopped. Changes are staged but not committed — 'git restore --staged .' to undo."; exit 0; }
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

git commit -m "$COMMIT_MSG"
git push

if $PARTIAL; then
  ok "Pushed partial update."
  exit 0
fi

if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
  warn "Tag v$NEW_VERSION already exists — not re-tagging."
else
  git tag "v$NEW_VERSION"
  git push origin "v$NEW_VERSION"
fi

ok "Pushed and tagged v$NEW_VERSION."
echo

# ---- poll the live site until the new version shows, rather than guessing how long to wait
PAGES_URL="https://bsc-sailing.github.io/calendar/"
info "Checking $PAGES_URL for v$NEW_VERSION (up to 2 minutes) ..."
for i in $(seq 1 12); do
  LIVE_VERSION="$(curl -fsSL "$PAGES_URL" 2>/dev/null | grep -o 'version: "[0-9][0-9.]*"' | head -n1 | grep -o '[0-9][0-9.]*' || true)"
  if [[ "$LIVE_VERSION" == "$NEW_VERSION" ]]; then
    ok "Live: v$LIVE_VERSION"
    exit 0
  fi
  sleep 10
done
warn "Still showing v${LIVE_VERSION:-unknown} after 2 minutes — GitHub Pages can be slow to rebuild. Check $PAGES_URL manually in a bit."
