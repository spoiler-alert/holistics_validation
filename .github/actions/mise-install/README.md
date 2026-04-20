# Mise Install Action

A simple action to reduce duplicated effort in installing mise and any actual packages

Supports caching (by default)

## Example

```yaml
    - uses: actions/checkout@v6
    - uses: ./.github/actions/mise-install
    - uses: google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093
      with:
        credentials_json: ${{ secrets.gcp_credentials }}
    - run: |
        eval "$(~/.local/bin/mise activate bash)"
        pushd opentofu/staging > /dev/null || exit 1
        tofu init
        tofu apply -auto-approve
```

> As with all custom actions, we must run a checkout before attempting to reference the action.

## Inputs

|name|description|default|
|----|-----------|-------|
|`packages`|Specific packages to install, space-delimited (defaults to installing all packages defined in `.config/mise.toml`)|`''`|
|`cache-name`|Use a unique name for the cache|`${{ runner.os}}-mise-install`|
