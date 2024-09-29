import argparse

from holistics_validation.validators.sql_validator import run_sql_validation

def create_parser():
    parser = argparse.ArgumentParser(
                    prog='holistics_validation',
                    description='A command line tool for validating holistics code')
    
    subparsers = parser.add_subparsers(title = 'Available sub-commands', dest='command')
    parser_sql = subparsers.add_parser('sql', help = 'Validates all SQL fields in all models of the given project with a few exceptions:  \n - Will NOT validate AQL  \n - Will NOT validate sql models that reference other models or are parameterized \n - Will raise errors for aggregation types of count distinct and median')

    ## TODO - some of these will be repeated depending on the validation type, once we add additional validation options then this should be standardized 
    parser_sql.add_argument('--holistics_api_key', required=True)
    parser_sql.add_argument('--holistics_project_id', required=True)
    parser_sql.add_argument('--commit_oid', help='Takes precendence over branch name. Leaving both unspecified means it will test against production.') 
    parser_sql.add_argument('--branch_name', help='Used only if commit id is not specified. Leaving both unspecified means it will test against production.') 
    parser_sql.add_argument('--bq_project_name', required=True) ## assumes that you have a BQ config file set up, if this is ever generalized to other query enginers then engine should probably be a sub-command with different inputs
    parser_sql.add_argument('--overrides', 
                        help='Overrides do a blanket replace from one value to another in all SQL, useful for things like testing against a different data source.  Format of "orig_value_1:new_name_1,orig_name_2:new_name_2,etc".  Currently does not support using "," or ":" in the actual override values.')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'sql':
        run_sql_validation(
            'bigquery', ## TODO: shouldn't be hardcoded if generalize to other engines
            {'bq_project_name': args.bq_project_name}, ## TODO: shouldn't be hardcoded if generalize to other engines
            holistics_api_key = args.holistics_api_key, 
            holistics_project_id = args.holistics_project_id,
            commit_oid = args.commit_oid, 
            branch_name = args.branch_name,
            override_string = args.overrides
        )


if __name__ == '__main__':
    main()
    