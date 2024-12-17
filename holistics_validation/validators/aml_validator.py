from holistics_validation.holistics_api_client import validate_aml
from holistics_validation.logger import logger
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus

def run_aml_validation(holistics_base_url, holistics_api_key, commit_oid, branch_name):
    status = validate_aml(
        holistics_base_url = holistics_base_url,
        holistics_api_key = holistics_api_key, 
        commit_oid=commit_oid,
        branch_name=branch_name
    )

    if status == 'success':
        logger.info(f'AML Validation completed successfully')
    elif status == 'failure':
        logger.error(f"AML Validation failed")
        raise FailedValidation()
    else: 
        logger.error(f"Found an unexpected job status: '{status}'")
        raise UnexpectedJobStatus()

    return True