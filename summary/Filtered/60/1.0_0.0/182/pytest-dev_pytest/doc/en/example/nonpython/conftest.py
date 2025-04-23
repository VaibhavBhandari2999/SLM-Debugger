# content of conftest.py
import pytest


def pytest_collect_file(parent, fspath):
    if fspath.suffix == ".yaml" and fspath.name.startswith("test"):
        return YamlFile.from_parent(parent, path=fspath)


class YamlFile(pytest.File):
    def collect(self):
        # We need a yaml parser, e.g. PyYAML.
        import yaml

        raw = yaml.safe_load(self.path.open())
        for name, spec in sorted(raw.items()):
            yield YamlItem.from_parent(self, name=name, spec=spec)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        """
        Runs a series of tests based on the specifications provided in the `spec` dictionary. Each test checks if the key (name) matches the corresponding value in the dictionary. If a mismatch is found, a `YamlException` is raised with details of the key and value that caused the failure.
        
        Parameters:
        self (object): The object instance that contains the `spec` dictionary.
        
        Returns:
        None: The function does not return any value. It raises an exception if a test fails.
        """

        for name, value in sorted(self.spec.items()):
            # Some custom test execution (dumb example follows).
            if name != value:
                raise YamlException(self, name, value)

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, YamlException):
            return "\n".join(
                [
                    "usecase execution failed",
                    "   spec failed: {1!r}: {2!r}".format(*excinfo.value.args),
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, f"usecase: {self.name}"


class YamlException(Exception):
    """Custom exception for error reporting."""
