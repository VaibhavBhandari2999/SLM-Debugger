# content of conftest.py
import pytest


def pytest_collect_file(parent, fspath):
    if fspath.suffix == ".yaml" and fspath.name.startswith("test"):
        return YamlFile.from_parent(parent, path=fspath)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and yields YamlItem instances from a YAML file.
        
        This function reads a YAML file and processes its contents to yield YamlItem objects. Each YamlItem is created from a specified name and its corresponding specification in the YAML file.
        
        Parameters:
        self (object): The object instance that contains the path to the YAML file.
        
        Returns:
        generator: A generator that yields YamlItem objects for each entry in the YAML file.
        
        Key Parameters:
        - `path` (Path):
        """

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
        return self.path, 0, f"usecase: {self.name}"


class YamlException(Exception):
    """Custom exception for error reporting."""
