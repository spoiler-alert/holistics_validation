import pytest

from holistics_validation.tooling.publish_aml import run_publish_aml
from holistics_validation.exceptions import FailedPublish, UnexpectedJobStatus
from holistics_validation.tests.utils import FakeClient


def test_run_publish_aml_success():
    client = FakeClient(job_completion_status="success")
    result = run_publish_aml(client)
    print(result)
    assert result is True


def test_run_publish_aml_failure_raises_failed_publish():
    client = FakeClient(job_completion_status="failure")
    with pytest.raises(FailedPublish):
        run_publish_aml(client)


def test_run_publish_aml_unexpected_status_raises_unexpected_job_status():
    client = FakeClient(job_completion_status="unknown")
    with pytest.raises(UnexpectedJobStatus):
        run_publish_aml(client)
