# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and processes YAML files to generate a sequence of YamlItem objects.
        
        This function reads a YAML file and processes its contents to create a sequence of YamlItem objects. Each YamlItem represents a named entry in the YAML file.
        
        Parameters:
        self (obj): The object instance that contains the file path to be processed.
        
        Returns:
        generator: A generator that yields YamlItem objects, each representing a named entry in the YAML file.
        
        Dependencies:
        - yaml: A Python
        """

        import yaml  # we need a yaml parser, e.g. PyYAML

        raw = yaml.safe_load(self.fspath.open())
        for name, spec in sorted(raw.items()):
            yield YamlItem(name, self, spec)


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
                    "   spec failed: %r: %r" % excinfo.value.args[1:3],
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class YamlException(Exception):
    """ custom exception for error reporting. """
