# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return YamlFile.from_parent(parent, fspath=path)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and processes YAML files.
        
        This function reads a YAML file and processes its contents to yield `YamlItem` objects.
        
        Parameters:
        self (FilesystemPath): The file path object representing the YAML file to be processed.
        
        Returns:
        Iterator[YamlItem]: An iterator yielding `YamlItem` objects, each representing a key-value pair from the YAML file.
        
        Dependencies:
        - yaml: A Python library for parsing YAML files, e.g. PyYAML.
        
        Example:
        """

        import yaml  # we need a yaml parser, e.g. PyYAML

        raw = yaml.safe_load(self.fspath.open())
        for name, spec in sorted(raw.items()):
            yield YamlItem.from_parent(self, name=name, spec=spec)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        for name, value in sorted(self.spec.items()):
            # some custom test execution (dumb example follows)
            if name != value:
                raise YamlException(self, name, value)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, YamlException):
            return "\n".join(
                [
                    "usecase execution failed",
                    "   spec failed: {1!r}: {2!r}".format(*excinfo.value.args),
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: {}".format(self.name)


class YamlException(Exception):
    """ custom exception for error reporting. """
