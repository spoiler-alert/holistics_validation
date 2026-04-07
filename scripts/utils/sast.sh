#!/usr/bin/env bash
set -ou pipefail

DEBUG=${DEBUG:-false}
CI=${CI:-false}

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
			exit 0
			;;
		--ci)
			CI=true
			shift
			;;
		--debug)
			DEBUG=true
			shift
			;;
		*)
			echo "Invalid argument!"
			shift
			;;
	esac
done

START=$(date +%s)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "${SCRIPT_DIR}" > /dev/null || exit 1
pushd "$(git rev-parse --show-toplevel)" > /dev/null || exit 1

exit_code=0

# we use --no-git-ignore so .semgrepignore doesn't get overridden.
# If .semgrepignore gets overridden, we end up scanning large parts of .yarn, which is slow and useless
_OPTIONS="--disable-version-check --no-autofix --metrics off --error --no-git-ignore"
if [[ "${DEBUG}" == "true" ]]; then
	_OPTIONS+=" --verbose"
else
	_OPTIONS+=" -q"
fi
_RULESETS="$(yq eval '.rulesets[]' .semgrep_settings.yml | sed 's/^/ -c /' | xargs)"
_EXCLUDE="$(yq eval '.excluded[]' .semgrep_settings.yml | sed 's/^/ --exclude-rule /' | xargs)"

printf "\nSAST scan for security/functional issues..\n"
if [[ "${CI}" == "false" ]]; then
	nosem_lines=$(grep --exclude-dir={node_modules,.git,build,built,dist,docs,.mongo_data} nosemgrep "$(pwd)" -RI | grep -Evc "\.md:")
	printf "There are ~%s nosemgrep lines in the code base\n" "${nosem_lines}"
fi
ignored_rules=$(yq eval '.excluded | length' .semgrep_settings.yml)
rulesets=$(yq eval '.rulesets | length' .semgrep_settings.yml)
printf "There are %s ignored rules from %s rulesets\n\n" "${ignored_rules}" "${rulesets}"

# shellcheck disable=SC2086
semgrep scan ${_OPTIONS} ${_RULESETS} ${_EXCLUDE} .
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
