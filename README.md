# holistics_validation

## Installation: 

You can install it by doing either of the following:
- Run `pip install git+ssh://git@github.com/spoiler-alert/holistics_validation.git`
- Add `git+ssh://git@github.com/spoiler-alert/holistics_validation.git` to your requirements.txt

For now, we don't support versions so this will pull the most up-to-date version from the main branch.  

## General Usage: 

Run `holistics_validation` followed by the type of validation you want.  Arguments that can be used for all types of validation: 
- `holistics_api_key` (required)
- `holistics_project_id` (required)
- `commit_oid` (optional): takes priority over branch_name if both are specified
- `branch_name` (optional): used only if commit_oid is NOT specified

NOTE: if NEITHER commit_oid or branch_name are specified, then it runs against production

## Validation Options:

### SQL Validation 

Validates all SQL fields using the specified SQL engine.  Run `holistics_validation sql`.  

Arguments for SQL validation, regardless of SQL engine: 
- `overrides` (optional): Overrides do a blanket replace from one value to another in all SQL, useful for things like testing against a different data source.  Format of "orig_value_1:new_name_1,orig_name_2:new_name_2,etc".  Currently does not support using "," or ":" in the actual override values.  Certain characters will need to be escaped (ex. if you're using \` then you will need to escape it with a \\).  

Currently supports the following SQL engines:

- BigQuery
  - Recommended auth methods: 
    - for local, use `gcloud auth application-default login` 
    - for non-local set up a service account, create a service account key and add it to the environment, and set an env var of `GOOGLE_APPLICATION_CREDENTIALS` as the path of the json file with the service account key 
  - Arguments:
    - `bq_project_name` (required)

### AML Validation

TODO: Needs endpoint from holistics

Intended to cover:
- Models
- Datasets
- Canvas Dashboards

### Content Validation

TODO: Needs endpoint from holistics

Intended to cover if a code change would break:
- Legacy Dashboards
- Alerts
- Schedules
- Embed Link

## TODO: 
- Automated testing - required to pass before merging
- Versions
- Do we want to open-source this?  If so, it needs some more generalization and improvements, plus adding to pypi

