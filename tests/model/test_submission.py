import pytest

from pysdmx.model.submission import SubmissionResult


@pytest.fixture
def action():
    return "Append"


@pytest.fixture
def short_urn():
    return "Codelist=BIS:BIS_DER(1.0)"


@pytest.fixture
def status():
    return "Success"


def test_full_instantiation(action, short_urn, status):
    submission_result = SubmissionResult(action, short_urn, status)

    assert submission_result.action == action
    assert submission_result.short_urn == short_urn
    assert submission_result.status == status
    assert str(submission_result) == f'action: {action}, short_urn: {short_urn}, status: {status}'
