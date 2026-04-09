#!/usr/bin/env bash

set -ou pipefail

running_id=$(id -urn)
if [[ "${running_id}" == "root" ]]; then
	echo "DO NOT RUN THIS SCRIPT AS ROOT!"
	exit 1
fi

while (($#)); do
	case $1 in
		--help|-help|help|--h|-h)
			echo "Usage: $0 [-h|--help]"
			echo "This script configures a local machine to work effectively with the spoileralert repo"
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
GIT_DIR=$(git rev-parse --show-toplevel)
pushd "${GIT_DIR}" > /dev/null || exit 1

if date --version > /dev/null 2>&1; then
	SYSTEM="gnu"
else
	SYSTEM="darwin"
fi
set -e

if [[ "${SYSTEM}" == "darwin" ]]; then
	echo "Configuring OS X!"
	echo "You may be prompted for your password during this script..."
	# no-op to cache privileges
	sudo -l > /dev/null
	if ! command -v brew &> /dev/null; then
		echo "Homebrew not found. Installing Homebrew..."
		# nosemgrep: bash.curl.security.curl-pipe-bash.curl-pipe-bash
		NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		echo "Homebrew installed successfully."
	else
		brew update
	fi
	brew install mise
	set +e
	# shellcheck disable=SC2016
	if ! grep -q 'eval "$(mise activate zsh --shims)"' "$HOME/.zshrc"; then
		# shellcheck disable=SC2016
		echo 'eval "$(mise activate zsh --shims)"' >> "$HOME/.zshrc"
	fi
	eval "$(mise activate zsh --shims)"
	# shellcheck disable=SC2016
	if ! grep -q 'autoload -Uz compinit && compinit' "$HOME/.zshrc"; then
		echo 'autoload -Uz compinit && compinit' >> "$HOME/.zshrc"
	fi
	# shellcheck disable=SC2016
	if ! grep -q 'MISE_EXPERIMENTAL=1' "$HOME/.zshrc"; then
		echo "MISE_EXPERIMENTAL=1" >> "$HOME/.zshrc"
	fi
	set -e
	sudo mkdir -p /usr/local/share/zsh/site-functions
	# we need this here to avoid a initial interaction
	mise trust --quiet .config/mise.toml
	mise completion zsh | sudo tee /usr/local/share/zsh/site-functions/_mise > /dev/null
else
	echo "Configuring Debian/Ubuntu!"

	arch=$(uname -m)
	if [[ "${arch}" == "x86_64" ]]; then
		arch="amd64"
	fi
	DEBIAN_FRONTEND=noninteractive
	export DEBIAN_FRONTEND
	sudo mkdir -p /etc/apt/keyrings

	curl -fSsL https://mise.jdx.dev/gpg-key.pub | gpg --dearmor | sudo tee /etc/apt/keyrings/mise-archive-keyring.gpg 1> /dev/null
	# shellcheck disable=SC1091
	echo "deb [signed-by=/etc/apt/keyrings/mise-archive-keyring.gpg] https://mise.jdx.dev/deb stable main" | sudo tee /etc/apt/sources.list.d/mise.list > /dev/null
	sudo apt-get update -qq
	sudo apt-get install -yqq mise
	set +e
	# shellcheck disable=SC2016
	if ! grep -q 'eval "$(mise activate bash --shims)"' "$HOME/.bashrc"; then
		# shellcheck disable=SC2016
		echo 'eval "$(mise activate bash --shims)"' >> "$HOME/.bashrc"
	fi
	# shellcheck disable=SC2016
	if ! grep -q 'MISE_EXPERIMENTAL=1' "$HOME/.bashrc"; then
		echo "MISE_EXPERIMENTAL=1" >> "$HOME/.bashrc"
	fi
	set -e
	eval "$(mise activate bash --shims)"

	mkdir -p "$HOME/.local/share/bash-completion/completions"
	# we need this here to avoid a initial interaction
	mise trust --quiet .config/mise.toml
	mise completion bash --include-bash-completion-lib > "$HOME/.local/share/bash-completion/completions/mise"
fi

echo "General Configuration..."

mise upgrade --yes

echo "Pre-commit hooks..."
lefthook install -f
lefthook run pre-commit --all-files

printf "\n\n***You may need to close and open your terminal for some commands to work consistently.***\n\n"

echo "Bootstrap run completed at $(date)"

popd > /dev/null || exit 1
popd > /dev/null || exit 1
