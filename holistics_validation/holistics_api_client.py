import requests
import time

from holistics_validation.exceptions import BadAPIResponse
from holistics_validation.logger import logger


class HolisticsAPIClient:
    def __init__(self, holistics_base_url, holistics_api_key):
        self.holistics_base_url = holistics_base_url
        self.headers = {"X-Holistics-Key": holistics_api_key, "Content-Type": "application/json"}

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.session.close()

    def parse_response(self, request_job):
        logger.debug("Status code: %s", request_job.status_code)
        if request_job.status_code != 200:
            logger.error(
                'Got an unexpected API response status code %i: "%s" and the message "%s"',
                request_job.status_code,
                request_job.reason,
                request_job.text,
            )
            raise BadAPIResponse()
        return request_job.json()

    def retrieve_model_fields(self, holistics_project_id, commit_oid=None, branch_name=None):

        endpoint = "data_models"
        request_url = self.holistics_base_url + endpoint

        if commit_oid:
            query_params = {"project_id": holistics_project_id, "commit_oid": commit_oid}
        elif branch_name:
            query_params = {"project_id": holistics_project_id, "branch_name": branch_name}
        else:
            query_params = {"project_id": holistics_project_id}

        logger.debug('Attempting request against "%s" using the following query params: %s', request_url, query_params)
        request_job = self.session.get(request_url, headers=self.headers, params=query_params)
        data = self.parse_response(request_job)

        return data

    def check_job_completion(self, job_id):

        endpoint = f"jobs/{job_id}"
        request_url = self.holistics_base_url + endpoint

        logger.info("Checking status of job: %s", job_id)

        tries = 1
        while True:
            logger.debug('Attempting request against "%s"', request_url)
            request_job = self.session.get(request_url, headers=self.headers)
            data = self.parse_response(request_job)
            status = data["job"]["status"]
            logger.debug("Status: %s", status)
            if status in ("success", "failure"):
                break
            else:
                tries += 1
                if tries > 100:
                    logger.error("Timeout after 100 attempts and no response that was a success / failure")
                    raise TimeoutError(
                        "Timing out after over 100 attempts and status of the job is still not in success / failure"
                    )
                time.sleep(2)

        return status, data["job"]["last_error_log"]

    def validate_aml(self, commit_oid, branch_name):

        endpoint = "aml_studio/projects/submit_validate"
        request_url = self.holistics_base_url + endpoint

        payload = {"commit_oid": commit_oid, "branch_name": branch_name}
        logger.debug('Attempting request against "%s" using the following payload: %s', request_url, payload)
        request_job = self.session.post(request_url, headers=self.headers, json=payload)
        data = self.parse_response(request_job)

        return data["job"]["id"]

    def publish_aml(self):

        endpoint = "aml_studio/projects/submit_publish"
        request_url = self.holistics_base_url + endpoint

        logger.debug('Attempting request against "%s"', request_url)
        request_job = self.session.post(request_url, headers=self.headers)
        data = self.parse_response(request_job)

        return data["job"]["id"]

    def preload_dashboard(self, dashboard_id):

        endpoint = f"dashboards/{dashboard_id}/submit_preload"
        request_url = self.holistics_base_url + endpoint

        logger.debug('Attempting request against "%s"', request_url)
        request_job = self.session.post(request_url, headers=self.headers)
        data = self.parse_response(request_job)

        return data["job"]["id"]
