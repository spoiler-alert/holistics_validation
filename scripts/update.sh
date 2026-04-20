#!/usr/bin/env bash

set -eou pipefail

running_id=$(id -urn)
if [[ "${running_id}" == "root" ]]; then
	echo "DO NOT RUN THIS SCRIPT AS ROOT!"
	exit 1
fi

while (($#)); do
	case $1 in
		--help|-help|help|--h|-h)
			echo "Usage: $0 [-h|--help]"
			echo "This script updates all local dependencies (infra containers, etc.) that are needed to launch our environment"
			echo
			echo "Arguments:"
			echo "-h|--help: Show this text"
			exit 0
			;;
		*)
			echo "Invalid argument!"
			shift
			;;
	esac
done

SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
pushd "${SCRIPT_DIR}" > /dev/null || exit 1
pushd "$(git rev-parse --show-toplevel)" > /dev/null || exit 1

echo "Upgrading local dependencies..."
mise upgrade --yes
mise prune --yes

echo "Synchronizing python deps..."
uv sync -U

popd > /dev/null || exit 1
popd > /dev/null || exit 1
