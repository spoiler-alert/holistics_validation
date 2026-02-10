import pytest

from holistics_validation.validators.dashboard_validator import run_dashboard_validation
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.tests.utils import FakeClient


def test_run_dashboard_validator_success():
    client = FakeClient(job_completion_status="success")
    result = run_dashboard_validation(client, "123")
    assert result is True


def test_run_dashboard_validator_failure_raises_failed_validation():
    client = FakeClient(job_completion_status="failure")
    with pytest.raises(FailedValidation):
        run_dashboard_validation(client, "123")


def test_run_dashboard_validator_unexpected_status_raises_unexpected_job_status():
    client = FakeClient(job_completion_status="unknown")
    with pytest.raises(UnexpectedJobStatus):
        run_dashboard_validation(client, "123")


def test_run_dashboard_validator_no_dashboards_ids():
    client = FakeClient(job_completion_status="success")
    with pytest.raises(ValueError):
        run_dashboard_validation(client, "")

def test_run_dashboard_validator_multiple_dashboard_ids(caplog):
    client = FakeClient(job_completion_status="success")
    result = run_dashboard_validation(client, "123, 456,\n789")
    assert result is True
    assert "Dashboard Validation for dashboard 123 completed successfully" in caplog.text
    assert "Dashboard Validation for dashboard 456 completed successfully" in caplog.text
    assert "Dashboard Validation for dashboard 789 completed successfully" in caplog.text

def test_run_dashboard_validator_report_multiple_failures(caplog):
    client = FakeClient(job_completion_status="failure")
    with pytest.raises(FailedValidation):
        run_dashboard_validation(client, "123, 456,\n789")
    assert "Dashboard Validation for dashboard 123 failed with the following error message: Test error message" in caplog.text
    assert "Dashboard Validation for dashboard 456 failed with the following error message: Test error message" in caplog.text
    assert "Dashboard Validation for dashboard 789 failed with the following error message: Test error message" in caplog.text
