import re

from holistics_validation.sql_engine_interfaces.bigquery_interface import BigQueryInterface
from holistics_validation.holistics_api_client import retrieve_model_fields

source_field_full_regex = r'{{ *#SOURCE\.\w+ *}}'
source_field_replace_regex = r'(?<=#SOURCE\.)\w+'
dependent_field_full_regex = r'{{ *\w+ *}}'
dependent_field_replace_regex = r'\w+(?= *}})'


sql_engine_interfaces = {
    'bigquery': BigQueryInterface
}

def parse_overrides(override_string):
    if not override_string:
        return []
    override_list = override_string.split(',')
    if not all([":" in x for x in override_list]):
        raise Exception("Expected ':' in override to separate before and after values, but didn't find any in at least one of the overrides")
    override_list = [x.split(':') for x in override_string.split(',')]
    return override_list


def run_sql_validation(sql_engine, credential_dict, holistics_api_key, holistics_project_id, commit_oid = None, branch_name = None, override_string = None):

    sql_interface_object = sql_engine_interfaces[sql_engine](credential_dict)
    overrides = parse_overrides(override_string)

    data = retrieve_model_fields(
        holistics_api_key = holistics_api_key, 
        holistics_project_id = holistics_project_id, 
        commit_oid=commit_oid,
        branch_name=branch_name
    )
    
    model_validations = []
    for model in data['data_models']:
        sql_validator = SQLValidator(sql_interface_object)
        model_validations.append(sql_validator)
        sql_validator.start_validation(model, overrides)

    for sql_validator in model_validations:
        sql_validator.check_validation()

    sql_interface_object.close_connection()

class SQLValidator():
    def __init__(self, sql_interface_object):
        self.sql_interface_object = sql_interface_object

    def start_validation(self, model, overrides = []):

        print(f"Starting validation of fields in model: {model['name']}")
        self.validation_jobs = {}

        if model['sql'] is None:
            short_table_name = model['table_name'].split('.')[-1]
            full_table_name = model['table_name']
            cte = ''
            for override in overrides:
                full_table_name = full_table_name.replace(override[0], override[1])
        else:
            if "{%" in model['sql'] or '{{' in model['sql']:
                print(f"We don't currently support validating parameterized queries or queries that reference other models, skipping validation for {model['name']}")
                return
            short_table_name = 'temp_table'
            full_table_name = 'temp_table'
            cte = self.sql_interface_object.cte.format(table_sql=model['sql'])
            for override in overrides:
                cte = cte.replace(override[0], override[1])

        dimensions, measures = self.create_field_dicts(model['dimensions'], model['measures'], short_table_name)
        for key, val in {'dimension': dimensions, 'measures': measures}.items():
            if len(val) > 0:
                query = self.sql_interface_object.base_query.format(cte = cte, fields = ',\n'.join(val), table = full_table_name) 

                self.validation_jobs[key] = {
                    'name': model['name'],
                    'job': self.sql_interface_object.start_job(query), 
                    'query': query, 
                    }
            else:
                print(f"No {key} found for {model['name']}, skipping validation for dimensions")

        return self.validation_jobs

    def replace_source_funtion(self, match_object):
        out = re.search(source_field_replace_regex, match_object.group(0))
        return f'{self.table_name}.{out.group(0)}'

    def replace_dependencies_funtion(self, match_object):
        out = re.search(dependent_field_replace_regex, match_object.group(0)).group(0)
        if out in self.field_dicts['dimensions']:
            val = self.field_dicts['dimensions'][out]
        elif out in self.field_dicts['measures']: 
            val = self.field_dicts['measures'][out]
        else:
            print(self.field_dicts['dimensions'])
            print(self.field_dicts['measures'])
            print(match_object)
            print(out)
            raise Exception("The field is in neither the list of dimensions or measures, ")
        return val

    def create_field_dicts(self, dimensions, measures, table_name):
        dependent_fields = {}
        input_dict = {
            'dimensions': dimensions,
            'measures': measures
        }
        self.field_dicts = {
            'dimensions': {},
            'measures': {}
        }
        self.table_name = table_name

        aggregation_dict = self.sql_interface_object.aggregation_dict

        ## if a field is independent, generate the sql for it, otherwise put it in a dict of dependent fields to be handled after  
        for j in ['dimensions', 'measures']:
            for i in range(len(input_dict[j])):
                if input_dict[j][i]['syntax'] == 'sql': 
                    field_sql = input_dict[j][i]['sql']
                    field_aggregation_type = input_dict[j][i]['aggregation_type']
                    field_transform_type = input_dict[j][i]['transform_type']
                    field_name = input_dict[j][i]['name']
                    if field_transform_type:
                        raise("We don't currently support transform type in the script, please either use something else or add it to the script") ## TODO
                    if j == 'dimensions' and field_aggregation_type:
                        raise("Aggregation type is not supported for dimensions") 
                    if j == 'measures' and field_aggregation_type != 'custom' :
                        if field_aggregation_type in aggregation_dict:
                            field_sql = f'{aggregation_dict[field_aggregation_type]}( {field_sql} )'
                        else:
                            raise Exception(f"We don't yet have logic for aggregation_type of '{field_aggregation_type}' in the validation script, please add it to this script or modify the field to use custom logic") 

                    ## only work on sql fields, since we can't easily convert AQL fields to sql
                    if re.search(source_field_full_regex, field_sql):
                        field_sql = re.sub(source_field_full_regex, self.replace_source_funtion, field_sql)
                    if "{{" in field_sql:
                        dependent_fields[field_name] = field_sql
                    else:
                        self.field_dicts[j][field_name] = field_sql

            ## handling the depending fields
            dependent_field_len = len(dependent_fields)
            while True:
                if len(dependent_fields) > 0:
                    fields_taken_care_of = []
                    for key, val in dependent_fields.items():
                        out = re.findall(dependent_field_replace_regex, val)
                        if all( (x in self.field_dicts['dimensions'] or x in self.field_dicts['measures']) for x in out):
                            field_sql = re.sub(dependent_field_full_regex, self.replace_dependencies_funtion, val)
                            self.field_dicts[j][key] = field_sql
                            fields_taken_care_of.append(key)
                    for i in fields_taken_care_of:
                        del dependent_fields[i]
                else:
                    break
                if len(dependent_fields) < dependent_field_len:
                    dependent_field_len = len(dependent_fields)
                else:
                    print(dependent_fields)
                    raise Exception("SQL fields remaining are dependent on either other fields that aren't defined in SQL (they could be defined as AQL, which would break)")

        return self.field_dicts['dimensions'].values(), self.field_dicts['measures'].values()

    def check_validation(self):
        for key, val in self.validation_jobs.items():
            try:
                print(f"Checking validation for {val['name']} {key}")
                self.sql_interface_object.check_job_results(val['job'])
            except Exception as e:
                print("Validation query failed, query that was run is below:")
                print(val['query'])
                raise e
            else:
                print(f"Successfully validated {val['name']} {key}")