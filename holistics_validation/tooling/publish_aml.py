from holistics_validation.exceptions import FailedPublish, UnexpectedJobStatus
from holistics_validation.holistics_api_client import HolisticsAPIClient
from holistics_validation.logger import logger
from holistics_validation.tests.utils import FakeAPIClient


def run_publish_aml(holistics_api_client: HolisticsAPIClient | FakeAPIClient) -> bool:
    """
    A function that takes in a holistics api client object and publishes
    the master branch for the corresponding holistics environment.

    The "completion" will show a failure if the publish fails, but we need to
    call the results to get the full list of errors that are blocking the publish
    """

    job_id = holistics_api_client.publish_aml()
    status, error_message = holistics_api_client.check_job_completion(job_id)

    if status == "success":
        logger.info("Publish AML completed successfully")
    elif status == "failure":
        result, errors = holistics_api_client.check_job_result(job_id)
        logger.error("Publish AML failed with an error message of '%s' and the following errors: %s", error_message, errors)
        raise FailedPublish()
    else:
        logger.error("Found an unexpected job status: '%s'", status)
        raise UnexpectedJobStatus()

    return True
