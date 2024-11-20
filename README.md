# holistics_validation

## Installation: 

You can install it by doing either of the following:
- Run `pip install git+ssh://git@github.com/spoiler-alert/holistics_validation.git`
- Add `git+ssh://git@github.com/spoiler-alert/holistics_validation.git` to your requirements.txt

For now, we don't support versions so doing the above will pull the most up-to-date version from the main branch.  

## General Usage: 

Run `holistics_validation` followed by the type of validation or job you want to run.  Arguments that can be used for all types of validation: 
- `holistics_base_url` (optional value): default value "https://us.holistics.io/api/v2/" when not included, ensure your URL ends with a `/`
- `holistics_api_key` (required)


## Validation Options:

### SQL Validation 

Validates all SQL fields using the specified SQL engine.  To use, run `holistics_validation sql`.  Relies on the endpoint [here](https://docs.holistics.io/api#tag/Data-Models/operation/DataModels_List).  

Arguments for SQL validation, regardless of SQL engine: 
- `holistics_project_id` (required)
- `commit_oid` (optional): takes priority over branch_name if both are specified
- `branch_name` (optional): used only if commit_oid is NOT specified, should be in the form of `origin/{branch_name}`
- `overrides` (optional): Overrides do a blanket replace from one value to another in all SQL, useful for things like testing against a different data source.  Format of "orig_value_1:new_value_1,orig_value_2:new_value_2,etc".  Currently does not support using "," or ":" in the actual override values.  Certain characters will need to be escaped (ex. if you're using \` then you will need to escape it with a \\).  

NOTE: if NEITHER commit_oid or branch_name are specified, then it runs against production

Currently supports the following SQL engines:

- BigQuery
  - Recommended auth methods: 
    - for local, use `gcloud auth application-default login` 
    - for non-local set up a service account, create a service account key and add it to the environment, and set an env var of `GOOGLE_APPLICATION_CREDENTIALS` as the path of the json file with the service account key 
  - Arguments:
    - `bq_project_name` (required)

### AML Validation

Validates all SQL fields using the specified SQL engine.  To use, run `holistics_validation aml`.  Arguments for AML validation: 
- `commit_oid` (required)
- `branch_name` (optional): should be in the form of `origin/{branch_name}`

Intended to cover:
- Models
- Datasets
- Canvas Dashboards

Known limitations:
- Compilation errors on widgets due to a modeling change (canvas or legacy dashboards)
- Dependency errors (ex. removed a field in a model, but the dataset or a canvas dashboard depend on it)

### Content Validation

TODO: Needs endpoint from holistics, has not been implemented

Intended to cover if a code change would break:
- Legacy Dashboards
- Alerts
- Schedules
- Embed Link

## Tooling Options:

In order to enable a full holistics CI/CD pipeline, this project is going to also include some tooling in addition to pure validation.  For now, this includes publishing, but might be expanded in the future.  

### Publish

Publishes any code that is merged into the master branch.  To use, run `holistics_validation publish`.  There are no additional arguments specific to only the publish command.  


## TODO: 
- Versions
- Add automated testing
- Do we want to open-source this?  If so, it needs some more generalization and improvements, plus adding to pypi