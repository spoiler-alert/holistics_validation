#!/usr/bin/env bash

set -eou pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "${SCRIPT_DIR}" > /dev/null || exit 1
pushd "$(git rev-parse --show-toplevel)" > /dev/null || exit 1

set +e
directories=$(find . -type f -name "pyproject.toml" -print0 2>/dev/null | xargs -0)
set -e

exit_code=0
for dir in ${directories}; do
	dir_path=$(dirname -- "${dir}")
	echo "Processing ${dir_path}..."
	pushd "${dir_path}" > /dev/null || exit 1
	if [[ -s uv.lock ]]; then
		uv sync --frozen -q
	else
		uv sync -q
	fi
	set +e
	ty check
	res=$?
	set -e
	if [[ "${res}" -ne 0 ]]; then
		exit_code=1
	fi
	popd > /dev/null || exit 1
done

popd > /dev/null || exit 1
popd > /dev/null || exit 1
exit "${exit_code}"
