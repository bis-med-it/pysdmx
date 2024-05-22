import pytest

from pysdmx.model.message import SubmissionResult


@pytest.fixture()
def action():
    return "Append"


@pytest.fixture()
def full_id():
    return "BIS:BIS_DER(1.0)"


@pytest.fixture()
def status():
    return "Success"


def test_full_instantiation(action, full_id, status):
    submission_result = SubmissionResult(action, full_id, status)

    assert submission_result.action == action
    assert submission_result.full_id == full_id
    assert submission_result.status == status
    assert str(submission_result) == (
        f"<Submission Result - Action: {action} "
        f"- Full ID: {full_id} "
        f"- Status: {status}>"
    )
