# Security

## Reporting Security Issues

While basic dependency checking is managed, please report any security issues in the issue tracker.

## Running all defined scans

Within a repo, we can quickly run all defined security scans:

```bash
scripts/utils/sast.sh
scripts/utils/secrets.sh
```

## Static Code Analysis

Static Code Analysis allows us to automatically catch obvious potential code issues around security and best practices. By running these initial scans, we can ensure a level of consistent code security and quality. We currently leverage [semgrep](https://semgrep.dev) to perform basic static code analysis scans.

### Quick OWASP Check against a repository

At the root of the repository (so once you've cloned it from whatever forge):

```bash
semgrep scan --no-autofix --config p/owasp-top-ten
```

### Manual Runs of semgrep

You can manually execute a full scan with semgrep like so:

```bash
scripts/utils/sast.sh
```

### Ignoring specific semgrep failures

Ideally we should _fix_ code problems that semgrep discovers, but there are times when the discovery is either inaccurate or not applicable. In those cases, we can [use the docs to understand how to ignore the alert](https://semgrep.dev/docs/ignoring-files-folders-code/)

Essentially, we can add `# nosemgrep: <rule name>` above a particular line in a file and semgrep will ignore any errors on the following line.

To ignore multiple rules, we can simply add a comma-separated list (e.g. `// nosemgrep: rule1, rule2`)

#### Global ignores

##### Files

If we're certain that a particular file should _never_ be scanned, we can add it to `.semgrepignore` (which uses similar format to `.gitignore`). Good examples of files we already ignore are `secrets.env` and everything under `.git/`.

##### Rules

If we're certain that a particular rule should _never_ be applied, we can add it to `.semgrep_settings.yml`. There are some example ignored rules in the file already, so adding to it should be fairly straight forward.

### Managing rulesets

Our actual semgrep scans rely on `.semgrep_settings.yml` to define which rulesets to download and which rules to ignore globally. If, for example, your project does not use node.js, removing the node.js ruleset may speed up security scans for your project!

## Secret Scanning

We leverage [gitleaks](https://github.com/gitleaks/gitleaks/) for secret scanning. It combs through the entire commit history of the project to determine any committed secrets and alerts us of them.

### Manual Run of gitleaks

gitleaks can be run against the repo manually like so:

```bash
scripts/utils/secrets.sh
```
