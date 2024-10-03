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
        # Note: it says count distinct is supported, but I can't figure out how to call it as an aggregation type
        self.aggregation_dict = {
            'min': 'MIN',
            'max': 'MAX',
            'sum': 'SUM',
            'count': 'COUNT',
            'avg': 'AVG',
            'stdev': 'STDDEV_SAMP',
            'stdevp': 'STDDEV_POP',
            'var': 'VAR_SAMP',
            'varp': 'VAR_POP',
        }


    def start_job(self, query_string):
        return self.client.query(query_string) #returns the job, the job still needs to be validated
    
    def check_job_results(self, job):
        return job.result()
    
    def close_connection(self):
        pass #BQ doesn't need to close the connection