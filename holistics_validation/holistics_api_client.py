import requests

from holistics_validation.logger import logger

## TODO: the URL can vary, if we make opensource then this should be an input of the cli
BASE_API_URL = 'https://us.holistics.io/api/v2/{endpoint}'


def retrieve_model_fields(holistics_api_key, holistics_project_id, commit_oid = None, branch_name = None ):

    ENDPOINT = 'data_models'
    REQUEST_URL = BASE_API_URL.format(endpoint = ENDPOINT)

    if commit_oid:
        payload = {'project_id': holistics_project_id, 'commit_oid': commit_oid}
    elif branch_name:
        payload = {'project_id': holistics_project_id, 'branch_name': branch_name}
    else:
        payload = {'project_id': holistics_project_id}
    
    headers = {'X-Holistics-Key': holistics_api_key} 

    logger.info(f'Attempting request against "{REQUEST_URL}" using the following payload: {payload}')
    r = requests.get(REQUEST_URL, headers = headers, data = payload)
    data = r.json()
    return data
