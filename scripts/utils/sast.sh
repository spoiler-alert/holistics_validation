#!/usr/bin/env bash
set -ou pipefail

DEBUG=${DEBUG:-false}
CI=${CI:-false}
# kept outside the repo tree so the scan never picks the rules up as targets.
# (rule id prefixing is handled separately, by --no-rewrite-rule-ids below)
OPENGREP_VENDOR_DIR="${OPENGREP_VENDOR_DIR:-${HOME}/.cache/opengrep-vendored-rulesets}"
CLEAN_VENDOR=${CLEAN_VENDOR:-"false"}
VENDOR_DOWNLOAD=${VENDOR_DOWNLOAD:-"false"}
# empty means a full scan; otherwise only files changed since this commit are scanned
DIFF_BASE=""

while (($#)); do
	case $1 in
		--help|-help|help|--h|-h)
			echo "Usage: $0 [-h|--help]"
			echo "This script triggers a run of our SAST scanner"
			echo
			echo "Arguments:"
			echo "-h|--help: Show this text"
			echo "--ci: Running in a CI environment"
			echo "--debug: Add debug information to output"
			echo "--diff-base <sha>: Only scan files changed since <sha> (default: full scan; in CI, non-main pushes diff against origin/main)"
			echo "--vendor-download: (Re-)fetch rulesets from the registry into OPENGREP_VENDOR_DIR"
			echo "--clean-vendor-dir: Remove OPENGREP_VENDOR_DIR before scanning (fails unless combined with --vendor-download)"
			exit 0
			;;
		--ci)
			CI=true
			shift
			;;
		--clean-vendor-dir)
			CLEAN_VENDOR="true"
			shift
			;;
		--vendor-download)
			VENDOR_DOWNLOAD="true"
			shift
			;;
		--debug)
			DEBUG=true
			shift
			;;
		--diff-base)
			if [[ -z "${2:-}" ]]; then
				echo "--diff-base requires a commit"
				exit 1
			fi
			DIFF_BASE="$2"
			shift 2
			;;
		*)
			echo "Invalid argument!"
			shift
			;;
	esac
done

vendor_rulesets() {
	_TMP_DIR="$(mktemp -d)"
	trap 'rm -rf "${_TMP_DIR}"' EXIT

	ignored_rules=$(yq eval '.excluded | length' .opengrep_settings.yml)
	rulesets=$(yq eval '.rulesets | length' .opengrep_settings.yml)
	printf "There are %s ignored rules from %s rulesets\n\n" "${ignored_rules}" "${rulesets}"
	mapfile -t _RAW_RULESETS < <(yq eval '.rulesets[]' .opengrep_settings.yml)

	printf "Fetching %s rulesets...\n" "${#_RAW_RULESETS[@]}"

	_FETCHED_FILES=()
	for ruleset in "${_RAW_RULESETS[@]}"; do
		dest="${_TMP_DIR}/${ruleset//\//-}.yml"
		if ! curl -sSfL --retry 3 --retry-delay 2 "https://semgrep.dev/c/${ruleset}" -o "${dest}"; then
			echo "Failed to fetch ruleset '${ruleset}' from the registry!"
			exit 1
		fi
		_FETCHED_FILES+=("${dest}")
	done

	# rulesets overlap, and duplicate rule ids make opengrep log a lot of
	# "Duplicated rule id" noise, so de-duplicate up front. unique_by keeps the first occurrence, so
	# earlier-listed rulesets win ties, matching the precedence rulesets already had.
	# each rule gets its own file, for debuggability. split by $index first (yq's
	# -s silently corrupts a handful of documents when the split expression itself
	# references a field from the piped document, e.g. the rule's own id), then
	# rename each file from its own (now static, already-written) content in a
	# second pass -- rule ids only ever contain filesystem-safe characters and are
	# already unique, so this can't collide.
	_TOTAL_BEFORE=0
	for f in "${_FETCHED_FILES[@]}"; do
		_TOTAL_BEFORE=$((_TOTAL_BEFORE + $(yq eval '.rules | length' "${f}")))
	done

	rm -rf "${OPENGREP_VENDOR_DIR}"
	mkdir -p "${OPENGREP_VENDOR_DIR}"
	# newer yq rejects split-exp output paths outside the cwd (the vendor dir is
	# deliberately outside the repo), so opt in explicitly
	yq --security-allow-write-any-path -s "\"${OPENGREP_VENDOR_DIR}/rule-\" + (\$index | tostring)" eval-all \
		'[.] | map(.rules) | flatten | unique_by(.id) | .[] | {"rules": [.]}' \
		"${_FETCHED_FILES[@]}"
	for f in "${OPENGREP_VENDOR_DIR}"/rule-*.yml; do
		id="$(yq eval '.rules[0].id' "${f}")"
		mv "${f}" "${OPENGREP_VENDOR_DIR}/${id}.yml"
	done

	_TOTAL_AFTER=$(find "${OPENGREP_VENDOR_DIR}" -maxdepth 1 -name '*.yml' | wc -l)

	printf "Vendored %s unique rules (%s duplicates removed) to %s, one rule per file\n" \
		"${_TOTAL_AFTER}" "$((_TOTAL_BEFORE - _TOTAL_AFTER))" "${OPENGREP_VENDOR_DIR}"
}

_vendor_dir_empty() {
	[[ ! -d "${OPENGREP_VENDOR_DIR}" ]] || [[ -n $(find "${OPENGREP_VENDOR_DIR}" -prune -empty 2>/dev/null) ]]
}

START=$(date +%s)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "${SCRIPT_DIR}" > /dev/null || exit 1
pushd "$(git rev-parse --show-toplevel)" > /dev/null || exit 1

# shellcheck source=scripts/utils/.library.sh
. scripts/utils/.library.sh
# the library turns on `set -e`, but this script inspects exit codes itself
set +e
# in CI, non-main pushes only scan their own changes (see scan_base in the library)
if [[ "${CI}" == "true" ]] && [[ -z "${DIFF_BASE}" ]]; then
	DIFF_BASE="$(scan_base)"
fi

if [[ "${CLEAN_VENDOR}" == "true" ]]; then
	rm -rf "${OPENGREP_VENDOR_DIR}"
fi
if [[ "${VENDOR_DOWNLOAD}" == "true" ]]; then
	# self-healing: fills an empty/missing dir (e.g. a first-ever run, or a
	# cache-miss), but is a no-op on an already-populated one, so callers can
	# pass --vendor-download unconditionally on every run without forcing a
	# live registry fetch every time. --clean-vendor-dir (above) empties the
	# dir first, so combining both flags forces a genuine refresh.
	if _vendor_dir_empty; then
		vendor_rulesets
	else
		echo "Vendor dir ${OPENGREP_VENDOR_DIR} is already populated, skipping download (pass --clean-vendor-dir to force a refresh)"
	fi
fi

if _vendor_dir_empty; then
	echo "No opengrep rules downloaded to ${OPENGREP_VENDOR_DIR}. Please re-run with --vendor-download"
	exit 1
fi
exit_code=0

# we use --no-git-ignore so .semgrepignore doesn't get overridden.
# If .semgrepignore gets overridden, we end up scanning large parts of folders like .mongo_data, which is slow and useless
_OPTIONS="--no-autofix --error --no-git-ignore --semgrepignore-filename=.opengrepignore --no-rewrite-rule-ids"
if [[ "${DEBUG}" == "true" ]]; then
	_OPTIONS+=" --verbose"
fi

_EXCLUDE="$(yq eval '.excluded[]' .opengrep_settings.yml | sed 's/^/ --exclude-rule /' | xargs)"

# Load vendored (local, de-duplicated) rulesets. The check above already
# guarantees OPENGREP_VENDOR_DIR exists and is non-empty by this point (or the
# script has already exited), so there's no live-registry fallback here.
# note: the vendor script writes one rule per file (de-duplicated across
# rulesets), loaded through a single `-c <directory>` flag. Opengrep 2.x
# prefixes rule ids with the config's path (breaking --exclude-rule matching),
# so --no-rewrite-rule-ids in _OPTIONS keeps them plain, e.g.
# `go.lang.security.injection.open-redirect.open-redirect`.
_RULESETS=" -c ${OPENGREP_VENDOR_DIR}"
printf "Using vendored rulesets from %s\n" "${OPENGREP_VENDOR_DIR}"

printf "\nSAST scan for security/functional issues..\n"
_exit=0
if [[ "${CI}" == "false" ]]; then
	nosem_lines=$(grep --exclude-dir={node_modules,.git,build,built,dist,docs,.mongo_data,.gcp-data,.valkey-data,.venv} -E "noopengrep|nosemgrep" "$(pwd)" -RI | grep -Evc "\.md:")
	printf "There are ~%s ignore lines in the code base\n" "${nosem_lines}"
else
	_OPTIONS+=" -q"
fi

_TARGETS=(.)
if [[ -n "${DIFF_BASE}" ]]; then
	# a new ruleset or removed exclusion can newly flag files we didn't touch, so that always gets a
	# full scan (ignore-file changes only shrink the scan, and the main/scheduled full scans backstop the rest)
	_SCAN_CONFIG=(.opengrep_settings.yml)
	if ! git cat-file -e "${DIFF_BASE}^{commit}" 2>/dev/null; then
		echo "Diff base ${DIFF_BASE} is not available, falling back to a full scan"
	elif ! git diff --quiet "${DIFF_BASE}" HEAD -- "${_SCAN_CONFIG[@]}"; then
		echo "SAST configuration changed since ${DIFF_BASE}, running a full scan"
	else
		mapfile -d '' -t _CHANGED < <(git diff --name-only -z --diff-filter=ACMR "${DIFF_BASE}" HEAD)
		# opengrep does not apply .opengrepignore to files named explicitly on the command line
		# (only to directories it walks), so drop ignored files here. .opengrepignore uses
		# gitignore syntax, so git can evaluate it for us.
		declare -A _IGNORED=()
		while IFS= read -r -d '' _f; do
			_IGNORED["${_f}"]=1
		done < <(printf '%s\0' "${_CHANGED[@]}" | git -c core.excludesFile="${PWD}/.opengrepignore" check-ignore --no-index -z --stdin)
		_TARGETS=()
		for _f in "${_CHANGED[@]}"; do
			[[ -z "${_IGNORED[${_f}]:-}" ]] && _TARGETS+=("${_f}")
		done
		if [[ "${#_TARGETS[@]}" -eq 0 ]]; then
			echo "No files changed since ${DIFF_BASE}, nothing to scan"
			exit 0
		fi
		printf "Scanning %s files changed since %s\n" "${#_TARGETS[@]}" "${DIFF_BASE}"
	fi
fi

# shellcheck disable=SC2086
opengrep scan ${_OPTIONS} ${_RULESETS} ${_EXCLUDE} "${_TARGETS[@]}"
_exit=$?

if [[ "${exit_code}" -eq 0 ]]; then
	exit_code="${_exit}"
fi

popd > /dev/null || exit 1
popd > /dev/null || exit 1

ended=$(date +%s)
elapsed=$((ended-START))
echo "SAST scan took ${elapsed} seconds"
if [[ "${exit_code}" -ne 0 ]]; then
	echo "A SCAN FAILED!"
fi
exit "${exit_code}"
