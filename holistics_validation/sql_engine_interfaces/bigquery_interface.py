from google.cloud import bigquery

## Notes: BQ allows you to start a job and check on it later so we can easily do it asynchronously, other sql engines might not work exactly the same


class BigQueryInterface:
    def __init__(self, credential_dict):

        self.client = bigquery.Client(project=credential_dict["bq_project_name"])

        ## TODO: edge case where dimensions are all aggregated - this would be a pretty extreme edge case, harder to handle than the reverse
        ## TODO: edge case where dimension is a JSON - it passes with with logic, but Holistics/BQ struggle to GROUP BY the field
        self.base_queries = {
            "dimensions": """
                {cte}

                SELECT 
                {fields}

                FROM {table}

                LIMIT 1;
                """,
            ## For measures, we want to add in a constant as the first field and group by it to account for the edge case of only measures that haven't been aggregated correctly
            "measures": """
                {cte}

                SELECT 
                1, 
                {fields}

                FROM {table}

                GROUP BY 1

                LIMIT 1;
                """,
        }

        self.cte = """
            WITH temp_table AS (
                {table_sql}
            )
            """

        # Note: 'median' uses a window function ex. `PERCENTILE_CONT ( field, 0.5 ) OVER (  )` - this is not easy to combine with other measures for this logic
        self.aggregation_dict = {
            "min": "MIN( {field} )",
            "max": "MAX( {field} )",
            "sum": "SUM( {field} )",
            "count": "COUNT( {field} )",
            "avg": "AVG( {field} )",
            "stdev": "STDDEV_SAMP( {field} )",
            "stdevp": "STDDEV_POP( {field} )",
            "var": "VAR_SAMP( {field} )",
            "varp": "VAR_POP( {field} )",
            "count distinct": "COUNT( DISTINCT {field} )",
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        pass  # BQ doesn't need to close the connection

    def start_job(self, query_string):
        return self.client.query(query_string)  # returns the job, the job still needs to be validated

    def check_job_results(self, job):
        return job.result()
