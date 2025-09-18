import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonNamePersonalisation
from pysdmx.model.vtl import NamePersonalisation


@pytest.fixture
def np():
    return NamePersonalisation(
        "NP1",
        name="Name Personalisation",
        description="Description",
        vtl_default_name="default_name",
        personalised_name="personalised_name",
        vtl_artefact="artefact",
    )


@pytest.fixture
def np_no_name():
    return NamePersonalisation(
        "NP1",
        vtl_default_name="default_name",
        personalised_name="personalised_name",
        vtl_artefact="artefact",
    )


def test_name_personalisation(np: NamePersonalisation):
    sjson = JsonNamePersonalisation.from_model(np)

    assert sjson.id == np.id
    assert sjson.name == np.name
    assert sjson.description == np.description
    assert len(sjson.annotations) == 0
    assert sjson.vtlDefaultName == np.vtl_default_name
    assert sjson.personalisedName == np.personalised_name
    assert sjson.vtlArtefact == np.vtl_artefact


def test_np_no_name(np_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonNamePersonalisation.from_model(np_no_name)
