from google.cloud import bigquery

## Notes: BQ allows you to start a job and check on it later so we can easily do it asynchronously, other sql engines might not work exactly the same 

class BigQueryInterface():
    def __init__(self, credential_dict):

        self.client = bigquery.Client(project=credential_dict['bq_project_name'])
        
        self.base_query = """
            {cte}

            SELECT 
            {fields}

            FROM {table}
            LIMIT 1;
            """
        
        self.cte = """
            WITH temp_table AS (
                {table_sql}
            )
            """
        
        # Note: 'median' uses a window function ex. `PERCENTILE_CONT ( field, 0.5 ) OVER (  )` - this breaks as a measure when combined with other measures
        self.aggregation_dict = {
            'min': 'MIN( {field} )',
            'max': 'MAX( {field} )',
            'sum': 'SUM( {field} )',
            'count': 'COUNT( {field} )',
            'avg': 'AVG( {field} )',
            'stdev': 'STDDEV_SAMP( {field} )',
            'stdevp': 'STDDEV_POP( {field} )',
            'var': 'VAR_SAMP( {field} )',
            'varp': 'VAR_POP( {field} )',
            'count distinct': 'COUNT( DISTINCT {field} )'
        }



    def start_job(self, query_string):
        return self.client.query(query_string) #returns the job, the job still needs to be validated
    
    def check_job_results(self, job):
        return job.result()
    
    def close_connection(self):
        pass #BQ doesn't need to close the connection