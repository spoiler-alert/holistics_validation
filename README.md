# holistics_validation

## Installation

You can install from GitHub by doing either of the following:

- Run `pip install git+ssh://git@github.com/spoiler-alert/holistics_validation.git`
- Add `git+ssh://git@github.com/spoiler-alert/holistics_validation.git` to your requirements.txt

For now, we don't support multiple versions so doing the above will pull the most up-to-date version from the main branch.

## General Usage

Run `holistics_validation` followed by the type of validation or job you want to run.  Arguments that can be used for all types of validation:

- `holistics_base_url` (optional value): default value `https://us.holistics.io/api/v2/` when not included, ensure your URL ends with a `/`
- `holistics_api_key` (required)

## Validation Options

### SQL Validation

Validates all SQL fields using the specified SQL engine.  To use, run `holistics_validation sql`.  [Relies on the endpoint here](https://docs.holistics.io/api#tag/Data-Models/operation/DataModels_List).

Arguments for SQL validation, regardless of SQL engine:

- `holistics_project_id` (required)
- `commit_oid` (optional): takes priority over branch_name if both are specified
- `branch_name` (optional): used only if commit_oid is NOT specified, should be in the form of `origin/{branch_name}`
- `overrides` (optional): Overrides do a blanket replace from one value to another in all SQL, useful for things like testing against a different data source.  Format of "orig_value_1:new_value_1,orig_value_2:new_value_2,etc".  Currently does not support using "," or ":" in the actual override values.  Certain characters will need to be escaped (ex. if you're using \` then you will need to escape it with a \\).

> if NEITHER commit_oid or branch_name are specified, then it runs against production

Currently supports the following SQL engines:

- BigQuery
  - Recommended auth methods:
    - for local, use `gcloud auth application-default login`
    - for non-local set up a service account, create a service account key and add it to the environment, and set an env var of `GOOGLE_APPLICATION_CREDENTIALS` as the path of the json file with the service account key
  - Arguments:
    - `bq_project_name` (required)

### AML Validation

Validates all SQL fields using the specified SQL engine.  To use, run `holistics_validation aml`.

Arguments for AML validation:

- `commit_oid` (required)
- `branch_name` (required): should be in the form of `origin/{branch_name}`

Intended to cover:

- Models
- Datasets
- Canvas Dashboards (v4)

Known limitations:

- Compilation errors on widgets due to a modeling change (both canvas and quick/legacy dashboards)
- Dependency errors (ex. removed a field in a model, but the dataset or a canvas dashboard depend on it)

### Reporting Validation

TODO: Needs endpoint from holistics, has not been implemented

**Please note:** this is different from Dashboard Validation!

[Reporting Validation](https://docs.holistics.io/docs/development/reporting-validation) matches functionality that holistics has for validating that code changes on your branch don't break already existing "Quick" or "Legacy" dashboards.

Intended to cover if a code change would break:

- Quick / Legacy Dashboards (v3)
- Alerts
- Schedules
- Embed Link

### Dashboard Validation

**Please note:** this is different from Reporting Validation!

Unlike the other validators, Dashboard Validation only applies to dashboards and code already published rather than testing a specific branch/commit.  It can be passed a list of dashboard IDs of any type of dashboard - a released canvas dashboard (v4) or a quick / legacy dashboard (v3) - and it will preload the dashboards (causing the SQL to be compiled and run), and reporting back any errors.  This is useful if holistics has released a change that broke pre-existing dashboards and you want to check a bunch of dashboards to see what's broken, or if a code change that breaks dashboards somehow got released without being caught.

Arguments for Dashboard Validation:

- `dashboard_ids` (required): comma separated list of the dashboard ID of either canvas dashboard or quick / legacy dashboards - this is the number in the URL when browsing a released dashboard

Intended to cover:

- Canvas Dashboards (v4)
- Quick / Legacy Dashboards (v3)

## Tooling Options

In order to enable a full holistics CI/CD pipeline, this project is going to also include some tooling in addition to pure validation.  For now, this includes publishing, but might be expanded in the future.

### Publish

Publishes any code that is merged into the master branch.  To use, run `holistics_validation publish`.  There are no additional arguments specific to only the publish command.

## Local Development

### Set-up

Initial setup on OS X and Linux can be achieved with just running `scripts/bootstrap.sh` after cloning the repo. This script should configure all local dependencies and ensure your system is ready to use the monorepo.

> `scripts/bootstrap.sh` only needs to be run infrequently. Daily work in the repo should _not_ require running `scripts/bootstrap.sh`.
> `scripts/bootstrap.sh` has only run successfully if a notification akin to "Bootstrap run completed at" appears on the screen.

This repo follows the [Scripts to Rule Them All](https://github.blog/engineering/engineering-principles/scripts-to-rule-them-all/) (STRTA) pattern. The idea being that relatively simple scripts can be configured that ensure a user's machine is able to effectively use a repo in a consistent manner.

### Linting, Formatting, and Type Checks

- Run `ruff format`
- Run `ruff check`
- Run `scripts/utils/python-type-check.sh`

### Testing

- Run `uv run pytest`

### WIP Installation

- Run `uv run holistics_validation --help` to test the cli functionality.

## TODO

- Write more tests
- Optional dependencies for SQL queries
- Versions
- API version probably shouldn't be in the base URL, but this is a breaking change and should have versions implemented first
