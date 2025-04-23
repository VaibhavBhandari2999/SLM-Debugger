# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return YamlFile.from_parent(parent, fspath=path)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects YamlItem instances from a YAML file.
        
        This function reads a YAML file and processes its contents to generate a sequence of YamlItem instances. Each item is associated with a name and a specification extracted from the YAML file.
        
        Parameters:
        self (FileLikeObject): The file-like object from which the YAML content is read.
        
        Returns:
        Iterable[YamlItem]: An iterable of YamlItem instances, each representing a key-value pair from the YAML file.
        
        Key Points:
        - The
        """

        # We need a yaml parser, e.g. PyYAML.
        import yaml

        raw = yaml.safe_load(self.fspath.open())
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
        return self.fspath, 0, f"usecase: {self.name}"


class YamlException(Exception):
    """Custom exception for error reporting."""
