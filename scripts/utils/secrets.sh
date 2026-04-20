#!/usr/bin/env bash

set -ou pipefail

CI=${CI:-false}
DEBUG=${DEBUG:-false}

while (($#)); do
	case $1 in
		--help|-help|help|--h|-h)
			echo "Usage: $0 [-h|--help]"
			echo "This script triggers a run of our secrets scanner"
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

echo "Scanning for secrets.."
gitleaks git
exit_code=$?

popd > /dev/null || exit 1
popd > /dev/null || exit 1

ended=$(date +%s)
elapsed=$((ended-START))
echo "Secret scan took ${elapsed} seconds"
if [[ "${exit_code}" -ne 0 ]]; then
	echo "A SCAN FAILED!"
fi
exit "${exit_code}"
