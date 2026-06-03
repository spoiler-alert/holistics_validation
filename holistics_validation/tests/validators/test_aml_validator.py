import pytest

from holistics_validation.validators.aml_validator import run_aml_validation
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.tests.utils import FakeAPIClient


def test_run_aml_validation_success(caplog):
    client = FakeAPIClient(job_completion_status="success", job_result="success")
    result = run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    assert result is True
    assert "AML Validation completed successfully and found no errors" in caplog.text


def test_run_aml_validation_job_run_failure(caplog):
    client = FakeAPIClient(job_completion_status="failure")
    with pytest.raises(FailedValidation):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    assert "AML Validation failed to run with the following error message: Test error message" in caplog.text


def test_run_aml_validation_job_run_unexpected_status(caplog):
    client = FakeAPIClient(job_completion_status="unknown")
    with pytest.raises(UnexpectedJobStatus):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    assert "Found an unexpected job status: 'unknown'" in caplog.text


def test_run_aml_validation_failure_raises_failed_validation(caplog):
    client = FakeAPIClient(job_completion_status="success", job_result="error")
    with pytest.raises(FailedValidation):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    assert "AML Validation found the following errors: Test error message - validation failed" in caplog.text


def test_run_aml_validation_unexpected_status_raises_unexpected_job_status(caplog):
    client = FakeAPIClient(job_completion_status="success", job_result="unknown")
    with pytest.raises(UnexpectedJobStatus):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    assert "Found an unexpected job result status: 'unknown'" in caplog.text


def test_run_aml_validation_missing_commit_oid():
    client = FakeAPIClient(job_completion_status="success", job_result="success")
    with pytest.raises(TypeError):
        run_aml_validation(client, branch_name="branch_name")  # ty: ignore[missing-argument]


def test_run_aml_validation_missing_branch_name():
    client = FakeAPIClient(job_completion_status="success", job_result="success")
    with pytest.raises(TypeError):
        run_aml_validation(client, commit_oid="commit_oid")  # ty: ignore[missing-argument]
