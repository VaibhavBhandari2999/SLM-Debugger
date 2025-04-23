# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and processes YAML files.
        
        This function reads a YAML file and processes its contents to yield `YamlItem` objects. Each item is a dictionary entry from the YAML file, where the key is the item's name and the value is the item's specification.
        
        Parameters:
        self (FilesystemPath): The file path object representing the YAML file to be processed.
        
        Returns:
        Iterator[YamlItem]: An iterator yielding `YamlItem` objects, each representing a processed entry from the
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
        """
        Runs a test for each item in the specification dictionary.
        
        This method iterates over the sorted items in the 'spec' dictionary. For each key-value pair, it performs a custom test where the key (name) is compared against the value. If the key and value do not match, a YamlException is raised with details about the mismatch.
        
        Parameters:
        self (object): The instance of the class containing the 'spec' dictionary.
        
        Returns:
        None: This method does not return any
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
