import pytest

from pysdmx.errors import PysdmxError
from pysdmx.model.__base import Annotation


@pytest.fixture
def id():
    return "AnnotationID"


@pytest.fixture
def title():
    return "Annotation 1"


@pytest.fixture
def text():
    return "A short text of the annotation."


@pytest.fixture
def url():
    return "http://example.com"


@pytest.fixture
def type():
    return "type"


def test_default(id):
    a = Annotation(id)

    assert a.id == id
    assert a.title is None
    assert a.text is None


def test_full_instantiation(id, title, text, url, type):
    a = Annotation(id, title, text, url, type)

    assert a.id == id
    assert a.title == title
    assert a.text == text
    assert a.url == url
    assert a.type == type


def test_equal(id, title, text):
    a1 = Annotation(id, title, text)
    a2 = Annotation(id, title, text)

    assert a1 == a2


def test_not_equal(id):
    a1 = Annotation(id)
    a2 = Annotation(id + id)

    assert a1 != a2


def test_tostr_id(id):
    a = Annotation(id)

    s = str(a)
    expected_str = f"id: {id}"

    assert s == expected_str


def test_tostr_all(id, title, text, url, type):
    a = Annotation(id=id, title=title, text=text, url=url, type=type)

    s = str(a)
    expected_str = f"id: {id}, title: {title}, text: {text}, url: {url}, type: {type}"

    assert s == expected_str


def test_torepr_id(id):
    a = Annotation(id)

    r = repr(a)
    expected_str = f"Annotation(id='{id}')"

    assert r == expected_str


def test_torepr_all(id, title, text, url, type):
    a = Annotation(id=id, title=title, text=text, url=url, type=type)

    r = repr(a)
    expected_str = (
        f"Annotation(id='{id}', title='{title}', text='{text}', "
        f"url='{url}', type='{type}')"
    )

    assert r == expected_str


def test_empty_annotation_not_allowed():
    with pytest.raises(PysdmxError, match="empty"):
        Annotation()
