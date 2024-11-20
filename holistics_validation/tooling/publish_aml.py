from holistics_validation.holistics_api_client import publish_aml
from holistics_validation.logger import logger
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus

def run_publish_aml(holistics_base_url, holistics_api_key):
    status = publish_aml(
        holistics_base_url = holistics_base_url,
        holistics_api_key = holistics_api_key
    )

    if status == 'success':
        logger.info(f'Publish AML completed successfully')
    elif status == 'failure':
        logger.error(f"Publish AML failed")
        raise FailedValidation()
    else: 
        logger.error(f"Found an unexpected job status: '{status}'")
        raise UnexpectedJobStatus()

    return True