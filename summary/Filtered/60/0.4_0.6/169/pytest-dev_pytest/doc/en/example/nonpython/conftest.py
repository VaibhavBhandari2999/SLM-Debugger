# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and yields YamlItem instances from a YAML file.
        
        This function reads a YAML file and processes its contents to generate YamlItem instances. Each item is yielded as it is processed.
        
        Parameters:
        self (FileLikeObject): An object representing the file path from which to read the YAML content.
        
        Returns:
        YamlItem: An iterator yielding YamlItem instances, each representing a key-value pair from the YAML file.
        
        Dependencies:
        - yaml: A Python library for parsing YAML
        """

        import yaml  # we need a yaml parser, e.g. PyYAML

        raw = yaml.safe_load(self.fspath.open())
        for name, spec in sorted(raw.items()):
            yield YamlItem(name, self, spec)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec

    def runtest(self):
        """
        Runs a series of tests based on the specifications provided in the `spec` dictionary.
        
        This method iterates over each key-value pair in the `spec` dictionary, where the key is the name of the test and the value is the expected result. It performs a custom test execution by comparing the name with the value. If the name and value do not match, a `YamlException` is raised.
        
        Parameters:
        self (object): The instance of the class containing the `spec` dictionary
        """

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
                    "   spec failed: %r: %r" % excinfo.value.args[1:3],
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class YamlException(Exception):
    """ custom exception for error reporting. """
