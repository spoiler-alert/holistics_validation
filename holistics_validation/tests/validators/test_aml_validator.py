import pytest

from holistics_validation.validators.aml_validator import run_aml_validation
from holistics_validation.exceptions import FailedValidation, UnexpectedJobStatus
from holistics_validation.tests.utils import FakeClient


def test_run_aml_validation_success():
    client = FakeClient(job_completion_status="success")
    result = run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")
    print(result)
    assert result is True


def test_run_aml_validation_failure_raises_failed_validation():
    client = FakeClient(job_completion_status="failure")
    with pytest.raises(FailedValidation):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")


def test_run_aml_validation_unexpected_status_raises_unexpected_job_status():
    client = FakeClient(job_completion_status="unknown")
    with pytest.raises(UnexpectedJobStatus):
        run_aml_validation(client, commit_oid="commit_oid", branch_name="branch_name")


def test_run_aml_validation_bad_or_missing_commit_oid():
    client = FakeClient(job_completion_status="success")
    with pytest.raises(TypeError):
        run_aml_validation(client, branch_name="branch_name")  # ty: ignore[missing-argument]


def test_run_aml_validation_no_branch_name():
    client = FakeClient(job_completion_status="success")
    with pytest.raises(TypeError):
        run_aml_validation(client, commit_oid="commit_oid")  # ty: ignore[missing-argument]
