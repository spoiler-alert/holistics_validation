from holistics_validation.logger import logger
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.holistics_api_client import HolisticsAPIClient


def run_aml_validation(
    holistics_api_client: HolisticsAPIClient, commit_oid: str, branch_name: str
) -> bool:
    """
    A function that takes in a holistics api client object as well as
    commit_oid and branch_name (in the form "origin/{branch_name}") and
    runs AML validation against it, reporting back if there's an error
    """

    job_id = holistics_api_client.validate_aml(
        commit_oid=commit_oid, branch_name=branch_name
    )
    status, error_message = holistics_api_client.check_job_completion(job_id)

    if status == "success":
        logger.info("AML Validation completed successfully")
    elif status == "failure":
        logger.error(
            "AML Validation failed with the following error message: %s", error_message
        )
        raise FailedValidation()
    else:
        logger.error("Found an unexpected job status: '%s'", status)
        raise UnexpectedJobStatus()

    return True
