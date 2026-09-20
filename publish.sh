#!/usr/bin/env bash
# Build the site and push it to GitHub. GitHub Pages redeploys within ~1 minute.
#
#   ./publish.sh                 build + commit + push (only if something changed)
#   ./publish.sh "message"       same, with a custom commit message
#   ./publish.sh --check         build only, no git (use before editing content)
#
# Safe to run from a scheduled task: exits 0 with "nothing to publish" when content is unchanged.
set -euo pipefail
cd "$(dirname "$0")"
LOG="publish.log"
stamp(){ date "+%Y-%m-%d %H:%M:%S"; }

python3 build.py || { echo "$(stamp) BUILD FAILED" >> "$LOG"; exit 1; }

if [[ "${1:-}" == "--check" ]]; then exit 0; fi

if [[ ! -d .git ]]; then
  echo "No git repo here yet. Run the setup steps in README.md first."; exit 1
fi

git add -A
if git diff --cached --quiet; then
  echo "$(stamp) checked — nothing to publish" >> "$LOG"
  echo "nothing to publish"; exit 0
fi

DATE=$(python3 -c "import json;print(json.load(open('content/site.json'))['meta']['data_date'])")
MSG="${1:-update site · data as of $DATE}"
git commit -q -m "$MSG"
git push -q origin HEAD
echo "$(stamp) published — $MSG" >> "$LOG"
echo "published: $MSG"
