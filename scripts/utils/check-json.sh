#!/usr/bin/env bash

set -eou pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "${SCRIPT_DIR}" > /dev/null || exit 1
pushd "$(git rev-parse --show-toplevel)" > /dev/null || exit 1

. scripts/utils/.library.sh

if [[ $# -eq 0 ]]; then
	FILES=$(git_files | grep "json$" | xargs)
else
	FILES=$*
fi

exit_code=0
for fn in ${FILES}; do
	echo "Checking ${fn}..."
	set +e
	jq '.' "${fn}" > /dev/null
	res=$?
	set -e
	if [[ "${res}" -ne 0 ]]; then
		exit_code=1
	fi
done

popd > /dev/null || exit 1
popd > /dev/null || exit 1
exit "${exit_code}"
