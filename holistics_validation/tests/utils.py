class FakeClient:
    def __init__(self, job_completion_status, holistics_base_url="test_url", holistics_api_key="test_api_key"):
        self.holistics_base_url = holistics_base_url
        self.job_completion_status = job_completion_status

    def retrieve_model_fields(self, holistics_project_id, commit_oid=None, branch_name=None):
        pass

    def check_job_completion(self, job_id):
        if self.job_completion_status == "success":
            return self.job_completion_status, None
        else:
            return self.job_completion_status, "Test error message"

    def validate_aml(self, commit_oid, branch_name):
        return "test_job_id"

    def publish_aml(self):
        return "test_job_id"

    def preload_dashboard(self, dashboard_id):
        return "test_job_id"
