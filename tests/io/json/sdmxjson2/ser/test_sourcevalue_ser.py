from pysdmx.io.json.sdmxjson2.messages.map import JsonSourceValue


def test_simple_value():
    value = "test"

    sjson = JsonSourceValue.from_model(value)

    assert sjson.value == value
    assert sjson.isRegEx is False


def test_regex_value():
    value = "regex:^test$"

    sjson = JsonSourceValue.from_model(value)

    assert sjson.value == "^test$"
    assert sjson.isRegEx is True
