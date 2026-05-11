from pysdmx.util import experimental


def test_experimental_function():
    @experimental
    class MyClass:
        """This is a test class."""

        pass

    assert MyClass.is_experimental is True
    assert "Warning: This class is experimental" in MyClass.__doc__
