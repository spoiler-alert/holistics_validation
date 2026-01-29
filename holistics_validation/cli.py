import argparse
import traceback

from holistics_validation.holistics_api_client import HolisticsAPIClient
from holistics_validation.validators.sql_validator import run_sql_validation
from holistics_validation.validators.aml_validator import run_aml_validation
from holistics_validation.validators.dashboard_validator import run_dashboard_validation
from holistics_validation.tooling.publish_aml import run_publish_aml
from holistics_validation.logger import logger

def generic_parser_add_args(parser):
    parser.add_argument('--holistics_base_url', default='https://us.holistics.io/api/v2/') 
    parser.add_argument('--holistics_api_key', required=True)

def sql_parser_add_args(parser):
    generic_parser_add_args(parser)
    parser.add_argument('--holistics_project_id', required=True)
    parser.add_argument('--commit_oid', help='Takes precendence over branch name. Leaving both unspecified means it will test against production.') 
    parser.add_argument('--branch_name', help='Used only if commit id is not specified. Leaving both unspecified means it will test against production.') 
    parser.add_argument('--bq_project_name', required=True) ## assumes that you have a BQ config file set up, if this is ever generalized to other query enginers then engine should probably be a sub-command with different inputs
    parser.add_argument('--overrides', 
                        help='Overrides do a blanket replace from one value to another in all SQL, useful for things like testing against a different data source.')

def aml_parser_add_args(parser):
    generic_parser_add_args(parser)
    parser.add_argument('--commit_oid', required=True) 
    parser.add_argument('--branch_name', required=True) 

def reporting_parser_add_args(parser):
    pass 

def dashboard_parser_add_args(parser):
    generic_parser_add_args(parser)
    parser.add_argument('--dashboard_ids', help='A single dashboard ID or comma separated list of dashboard IDs to validate', required=True) 

def publish_parser_add_args(parser):
    generic_parser_add_args(parser)

def create_parser():
    parser = argparse.ArgumentParser(
                    prog='holistics_validation',
                    description='A command line tool for validating holistics code')
    
    subparsers = parser.add_subparsers(title = 'Available sub-commands', dest='command')

    sql_parser = subparsers.add_parser('sql', help = 'Validates all SQL fields in all models of the given project with a few exceptions:  \n - Will NOT validate AQL  \n - Will NOT validate sql models that reference other models or are parameterized \n - Will raise errors for aggregation type of median')
    sql_parser_add_args(sql_parser)

    aml_parser = subparsers.add_parser('aml', help = 'Validates AML for the given commit oid and branch')
    aml_parser_add_args(aml_parser)

    reporting_parser = subparsers.add_parser('reporting', help = 'Validates if a given commit oid or branch will break any pre-existing quick / legacy dashboards')
    reporting_parser_add_args(reporting_parser)

    dashboard_parser = subparsers.add_parser('dashboard', help = 'Validates if the given dashboard(s) are broken')
    dashboard_parser_add_args(dashboard_parser)

    publish_parser = subparsers.add_parser('publish', help = 'Publishes master branch')
    publish_parser_add_args(publish_parser)
    
    return parser


def main():
    try: 
        parser = create_parser()
        args = parser.parse_args()

        api_client = HolisticsAPIClient(                
            holistics_base_url = args.holistics_base_url,
            holistics_api_key = args.holistics_api_key, 
        )

        if args.command == 'sql':
            run_sql_validation(
                'bigquery', ## TODO: shouldn't be hardcoded if generalize to other engines
                {'bq_project_name': args.bq_project_name}, ## TODO: shouldn't be hardcoded if generalize to other engines
                holistics_api_client = api_client, 
                holistics_project_id = args.holistics_project_id,
                commit_oid = args.commit_oid, 
                branch_name = args.branch_name,
                override_string = args.overrides,
            )

        if args.command == 'aml':
            run_aml_validation(
                holistics_api_client = api_client, 
                commit_oid = args.commit_oid, 
                branch_name = args.branch_name,
            )

        if args.command == 'reporting':
            raise NotImplementedError('Waiting for for holistics to add an API endpoint for reporting validation')

        if args.command == 'dashboard':
            run_dashboard_validation(
                holistics_api_client = api_client, 
                dashboard_ids = args.dashboard_ids
            )

        if args.command == 'publish':
            run_publish_aml(
                holistics_api_client = api_client, 
            )


    except Exception as e:
        logger.error(traceback.format_exc()) #ensures the error is logged in the log file and not just the console 
        raise e


if __name__ == '__main__':
    main()
    