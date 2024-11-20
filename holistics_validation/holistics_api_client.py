import requests
import time

from holistics_validation.logger import logger
from holistics_validation.exceptions import BadAPIResponse


def parse_response(request_job):
    logger.debug(f"Status code: {request_job.status_code}")
    if request_job.status_code != 200:
        logger.error(f'Got an unexpected API response status code {request_job.status_code}: "{request_job.reason}" and the message "{request_job.text}"')
        raise BadAPIResponse()
    return request_job.json()


def retrieve_model_fields(holistics_base_url, holistics_api_key, holistics_project_id, commit_oid = None, branch_name = None ):

    endpoint = 'data_models'
    request_url = holistics_base_url + endpoint

    if commit_oid:
        payload = {'project_id': holistics_project_id, 'commit_oid': commit_oid}
    elif branch_name:
        payload = {'project_id': holistics_project_id, 'branch_name': branch_name}
    else:
        payload = {'project_id': holistics_project_id}
    
    headers = {'X-Holistics-Key': holistics_api_key} 
    logger.debug(f'Attempting request against "{request_url}" using the following payload: {payload}')
    request_job = requests.get(request_url, headers = headers, data = payload)
    data = parse_response(request_job)

    return data


def check_job_completion(holistics_base_url, holistics_api_key, job_id):

    endpoint = f'jobs/{job_id}/result'
    request_url = holistics_base_url + endpoint

    logger.debug(f'Checking status of job: {job_id}')

    tries = 1
    while True:
        headers = {'X-Holistics-Key': holistics_api_key} 
        logger.debug(f'Attempting request against "{request_url}" with no payload')
        request_job = requests.get(request_url, headers = headers)
        data = parse_response(request_job)
        status = data['status']
        logger.debug(f"Status: {status}")
        if status in ('success', 'failure'):
            break
        else:
            tries += 1
            if tries > 100:
                logger.error("Timeout after 100 attempts and no response that was a success / failure")
                raise TimeoutError("Timing out after over 100 attempts and status of the job is still not in success / failure")
            time.sleep(2)
    
    return status


def validate_aml(holistics_base_url, holistics_api_key, commit_oid, branch_name):

    endpoint = 'aml_studio/projects/submit_validate'
    request_url = holistics_base_url + endpoint

    payload = {'commit_oid': commit_oid, 'branch_name': branch_name}
    headers = {'X-Holistics-Key': holistics_api_key} 
    logger.debug(f'Attempting request against "{request_url}" using the following payload: {payload}')
    request_job = requests.post(request_url, headers = headers, data = payload)
    data = parse_response(request_job)

    status = check_job_completion(holistics_base_url, holistics_api_key, data['job']['id'])
    return status

    

def publish_aml(holistics_base_url, holistics_api_key):

    endpoint = 'aml_studio/projects/submit_publish'
    request_url = holistics_base_url + endpoint

    headers = {'X-Holistics-Key': holistics_api_key, "Content-Type": "application/json"} 
    logger.debug(f'Attempting request against "{request_url}" with no payload')
    request_job = requests.post(request_url, headers = headers)
    data = parse_response(request_job)

    status = check_job_completion(holistics_base_url, holistics_api_key, data['job']['id'])
    return status
