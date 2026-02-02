from holistics_validation.logger import logger
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.holistics_api_client import HolisticsAPIClient

def run_dashboard_validation(
        holistics_api_client: HolisticsAPIClient, 
        dashboard_ids: str
    )->bool:

    """
    A function that takes in a holistics api client object as well as 
    dashboard_ids (a string where each dashboard ID is separated by commas, 
    either v3 or deployed v4 dashboards) and attempts to preload the dashboard
    using the code currently published and reports back with any errors on
    the widgets
    """

    dashboard_list = [d.strip() for d in dashboard_ids.split(',') if d.strip()]
    if not dashboard_list:
        raise ValueError("dashboard_ids must contain at least one non-empty dashboard id")    

    # starts all the jobs since waiting for the queries might take quite a while 
    dashboard_job_dict = {}
    for dashboard_id in dashboard_list:
        dashboard_job_dict[dashboard_id] = holistics_api_client.preload_dashboard(dashboard_id = dashboard_id)

    # checks jobs one by one - it's possible 
    failures = []
    unknown_status = []
    for dashboard_id, job_id in dashboard_job_dict.items():
        status, error_message = holistics_api_client.check_job_completion(job_id)
        if status == 'success':
            logger.info('Dashboard Validation for dashboard %s completed successfully', dashboard_id)
        elif status == 'failure':
            logger.error('Dashboard Validation for dashboard %s failed with the following error message: %s', dashboard_id, error_message)
            failures.append(dashboard_id)
        else: 
            logger.error("Dashboard Validation for dashboard %s found an unexpected job status: '%s'", dashboard_id, status)
            unknown_status.append(dashboard_id)

    if failures:
        raise FailedValidation()
    
    #This won't be called if there are any failures, but I think that's ok since they'll be looking at the logs
    if unknown_status: 
        raise UnexpectedJobStatus() 

    return True