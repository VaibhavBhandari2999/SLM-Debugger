# content of conftest.py
import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        """
        Collects and processes YAML files to generate a sequence of YamlItem objects.
        
        This function reads a YAML file and extracts items, yielding each as a YamlItem object.
        
        Parameters:
        self (FileLikeObject): The file-like object representing the YAML file to be processed.
        
        Returns:
        Iterator[YamlItem]: An iterator yielding YamlItem objects, each representing a key-value pair from the YAML file.
        
        Key Details:
        - The function uses `yaml.safe_load` to parse the YAML
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
        Runs a series of tests based on the specifications provided in the `spec` dictionary. Each test checks if the key (name) in the dictionary matches its corresponding value. If a mismatch is found, a `YamlException` is raised with details about the key and its value.
        
        Parameters:
        self (object): The object instance containing the `spec` dictionary.
        
        Returns:
        None: The function does not return any value. It raises an exception if a test fails.
        
        Example:
        ```
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
