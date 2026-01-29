from holistics_validation.logger import logger
from holistics_validation.exceptions import FailedPublish, UnexpectedJobStatus
from holistics_validation.holistics_api_client import HolisticsAPIClient

def run_publish_aml(holistics_api_client: HolisticsAPIClient) -> bool:

    """
    A function that takes in a holistics api client object and publishes 
    the master branch for the corresponding holistics environment
    """

    job_id = holistics_api_client.publish_aml()
    status, error_message = holistics_api_client.check_job_completion(job_id)

    if status == 'success':
        logger.info('Publish AML completed successfully')
    elif status == 'failure':
        logger.error("Publish AML failed with the following error message: %s", error_message)
        raise FailedPublish()
    else: 
        logger.error("Found an unexpected job status: '%s'", status)
        raise UnexpectedJobStatus()

    return True