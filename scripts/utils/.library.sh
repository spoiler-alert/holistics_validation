#!/usr/bin/env bash

set -eo pipefail
LC_ALL=C
export LC_ALL

function git_files {
	FILES=$(git ls-files --exclude-standard)
	FILES+=" $(git ls-files --exclude-standard --others)"
	echo "${FILES}"
}

# Prints the commit that sast.sh/secrets.sh should diff against (--diff-base).
# Prints nothing for a full scan: pushes to main, scheduled/manual runs, or when no merge-base
# with origin/main can be found (never skip a scan). Needs a checkout with fetch-depth: 0.
function scan_base {
	if [[ "${GITHUB_EVENT_NAME:-push}" == "push" && "${GITHUB_REF:-}" != "refs/heads/main" ]]; then
		git merge-base origin/main HEAD 2>/dev/null || true
	fi
}
