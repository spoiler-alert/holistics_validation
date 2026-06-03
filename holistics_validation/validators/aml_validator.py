from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.holistics_api_client import HolisticsAPIClient
from holistics_validation.logger import logger
from holistics_validation.tests.utils import FakeAPIClient


def run_aml_validation(holistics_api_client: HolisticsAPIClient | FakeAPIClient, commit_oid: str, branch_name: str) -> bool:
    """
    A function that takes in a holistics api client object as well as
    commit_oid and branch_name (in the form "origin/{branch_name}") and
    runs AML validation against it, reporting back if there's an error

    AML validation completion will show the job is a success if there are errors,
    but the job might fail due to a bug regardless of the AML being valid, which is
    why we're separating "completion" status check vs error check
    """

    job_id = holistics_api_client.validate_aml(commit_oid=commit_oid, branch_name=branch_name)
    status, error_message = holistics_api_client.check_job_completion(job_id)

    if status == "success":
        logger.info("AML Validation finished, checking for errors")
        result, errors = holistics_api_client.check_job_result(job_id, "errors")

        if result == "success":
            logger.info("AML Validation completed successfully and found no errors")
        elif result == "error":
            logger.info("AML Validation found the following errors: %s", errors)
            raise FailedValidation()
        else:
            logger.error("Found an unexpected job result status: '%s'", result)
            raise UnexpectedJobStatus()

    elif status == "failure":
        logger.error("AML Validation failed to run with the following error message: %s", error_message)
        raise FailedValidation()
    else:
        logger.error("Found an unexpected job status: '%s'", status)
        raise UnexpectedJobStatus()

    return True
