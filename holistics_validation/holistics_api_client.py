import requests

base_api_url = 'https://us.holistics.io/api/v2/{endpoint}'


def retrieve_model_fields(holistics_api_key, holistics_project_id, commit_oid = None, branch_name = None ):

    if commit_oid:
        payload = {'project_id': holistics_project_id, 'commit': commit_oid} # documentation says commit_oid, but I think it's actually commit
    else:
        payload = {'project_id': holistics_project_id, 'branch': branch_name} # documentation says branch_name, but I think it's actually branch

    headers = {'X-Holistics-Key': holistics_api_key} 

    r = requests.get(base_api_url.format(endpoint = 'data_models'), headers = headers, data = payload)
    data = r.json()
    return data
