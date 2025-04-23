from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import distutils.spawn
import os
import sys

import py

import pytest
from _pytest.config import argparsing as parseopt
from _pytest.config.exceptions import UsageError


@pytest.fixture
def parser():
    return parseopt.Parser()


class TestParser(object):
    def test_no_help_by_default(self):
        parser = parseopt.Parser(usage="xyz")
        pytest.raises(UsageError, lambda: parser.parse(["-h"]))

    def test_custom_prog(self, parser):
        """Custom prog can be set for `argparse.ArgumentParser`."""
        assert parser._getparser().prog == os.path.basename(sys.argv[0])
        parser.prog = "custom-prog"
        assert parser._getparser().prog == "custom-prog"

    def test_argument(self):
        with pytest.raises(parseopt.ArgumentError):
            # need a short or long option
            argument = parseopt.Argument()
        argument = parseopt.Argument("-t")
        assert argument._short_opts == ["-t"]
        assert argument._long_opts == []
        assert argument.dest == "t"
        argument = parseopt.Argument("-t", "--test")
        assert argument._short_opts == ["-t"]
        assert argument._long_opts == ["--test"]
        assert argument.dest == "test"
        argument = parseopt.Argument("-t", "--test", dest="abc")
        assert argument.dest == "abc"
        assert str(argument) == (
            "Argument(_short_opts: ['-t'], _long_opts: ['--test'], dest: 'abc')"
        )

    def test_argument_type(self):
        argument = parseopt.Argument("-t", dest="abc", type=int)
        assert argument.type is int
        argument = parseopt.Argument("-t", dest="abc", type=str)
        assert argument.type is str
        argument = parseopt.Argument("-t", dest="abc", type=float)
        assert argument.type is float
        with pytest.warns(DeprecationWarning):
            with pytest.raises(KeyError):
                argument = parseopt.Argument("-t", dest="abc", type="choice")
        argument = parseopt.Argument(
            "-t", dest="abc", type=str, choices=["red", "blue"]
        )
        assert argument.type is str

    def test_argument_processopt(self):
        """
        Tests the `Argument` class from the `parseopt` module.
        
        This function tests the `Argument` class by creating an instance with specific parameters and verifying its attributes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `type`: The type of the argument (int in this case).
        - `default`: The default value of the argument (42 in this case).
        - `dest`: The destination name for the argument ("abc" in this case).
        
        The
        """

        argument = parseopt.Argument("-t", type=int)
        argument.default = 42
        argument.dest = "abc"
        res = argument.attrs()
        assert res["default"] == 42
        assert res["dest"] == "abc"

    def test_group_add_and_get(self, parser):
        group = parser.getgroup("hello", description="desc")
        assert group.name == "hello"
        assert group.description == "desc"

    def test_getgroup_simple(self, parser):
        group = parser.getgroup("hello", description="desc")
        assert group.name == "hello"
        assert group.description == "desc"
        group2 = parser.getgroup("hello")
        assert group2 is group

    def test_group_ordering(self, parser):
        parser.getgroup("1")
        parser.getgroup("2")
        parser.getgroup("3", after="1")
        groups = parser._groups
        groups_names = [x.name for x in groups]
        assert groups_names == list("132")

    def test_group_addoption(self):
        group = parseopt.OptionGroup("hello")
        group.addoption("--option1", action="store_true")
        assert len(group.options) == 1
        assert isinstance(group.options[0], parseopt.Argument)

    def test_group_addoption_conflict(self):
        group = parseopt.OptionGroup("hello again")
        group.addoption("--option1", "--option-1", action="store_true")
        with pytest.raises(ValueError) as err:
            group.addoption("--option1", "--option-one", action="store_true")
        assert str({"--option1"}) in str(err.value)

    def test_group_shortopt_lowercase(self, parser):
        group = parser.getgroup("hello")
        with pytest.raises(ValueError):
            group.addoption("-x", action="store_true")
        assert len(group.options) == 0
        group._addoption("-x", action="store_true")
        assert len(group.options) == 1

    def test_parser_addoption(self, parser):
        """
        Test the parser's addoption method.
        
        This function checks if the `addoption` method of the `parser` object correctly adds a custom option to the specified group. The `parser` object is expected to have a `getgroup` method that retrieves a group by name. The `addoption` method is used to add a new option to the group. The function asserts that the group initially has no options and then adds the `--option1` option with the `store_true` action
        """

        group = parser.getgroup("custom options")
        assert len(group.options) == 0
        group.addoption("--option1", action="store_true")
        assert len(group.options) == 1

    def test_parse(self, parser):
        """
        Parse command-line arguments using the given parser.
        
        This function adds an option `--hello` to the parser, which stores the value of the option in the `hello` attribute of the parsed arguments. It then parses the command-line arguments `["--hello", "world"]` and asserts that the `hello` attribute is set to "world". Additionally, it checks that the `FILE_OR_DIR` attribute is not set.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which
        """

        parser.addoption("--hello", dest="hello", action="store")
        args = parser.parse(["--hello", "world"])
        assert args.hello == "world"
        assert not getattr(args, parseopt.FILE_OR_DIR)

    def test_parse2(self, parser):
        args = parser.parse([py.path.local()])
        assert getattr(args, parseopt.FILE_OR_DIR)[0] == py.path.local()

    def test_parse_known_args(self, parser):
        parser.parse_known_args([py.path.local()])
        parser.addoption("--hello", action="store_true")
        ns = parser.parse_known_args(["x", "--y", "--hello", "this"])
        assert ns.hello
        assert ns.file_or_dir == ["x"]

    def test_parse_known_and_unknown_args(self, parser):
        parser.addoption("--hello", action="store_true")
        ns, unknown = parser.parse_known_and_unknown_args(
            ["x", "--y", "--hello", "this"]
        )
        assert ns.hello
        assert ns.file_or_dir == ["x"]
        assert unknown == ["--y", "this"]

    def test_parse_will_set_default(self, parser):
        parser.addoption("--hello", dest="hello", default="x", action="store")
        option = parser.parse([])
        assert option.hello == "x"
        del option.hello
        parser.parse_setoption([], option)
        assert option.hello == "x"

    def test_parse_setoption(self, parser):
        parser.addoption("--hello", dest="hello", action="store")
        parser.addoption("--world", dest="world", default=42)

        class A(object):
            pass

        option = A()
        args = parser.parse_setoption(["--hello", "world"], option)
        assert option.hello == "world"
        assert option.world == 42
        assert not args

    def test_parse_special_destination(self, parser):
        parser.addoption("--ultimate-answer", type=int)
        args = parser.parse(["--ultimate-answer", "42"])
        assert args.ultimate_answer == 42

    def test_parse_split_positional_arguments(self, parser):
        parser.addoption("-R", action="store_true")
        parser.addoption("-S", action="store_false")
        args = parser.parse(["-R", "4", "2", "-S"])
        assert getattr(args, parseopt.FILE_OR_DIR) == ["4", "2"]
        args = parser.parse(["-R", "-S", "4", "2", "-R"])
        assert getattr(args, parseopt.FILE_OR_DIR) == ["4", "2"]
        assert args.R is True
        assert args.S is False
        args = parser.parse(["-R", "4", "-S", "2"])
        assert getattr(args, parseopt.FILE_OR_DIR) == ["4", "2"]
        assert args.R is True
        assert args.S is False

    def test_parse_defaultgetter(self):
        def defaultget(option):
            """
            Function to set default values for options based on their type.
            
            Parameters:
            option (Option): The option for which to set the default value.
            
            Returns:
            None: This function does not return anything. It modifies the 'default' attribute of the provided option in place.
            
            This function checks if the provided option has a 'type' attribute. If it does, it sets the 'default' attribute of the option based on the type:
            - If the type is int, the default value is set
            """

            if not hasattr(option, "type"):
                return
            if option.type is int:
                option.default = 42
            elif option.type is str:
                option.default = "world"

        parser = parseopt.Parser(processopt=defaultget)
        parser.addoption("--this", dest="this", type=int, action="store")
        parser.addoption("--hello", dest="hello", type=str, action="store")
        parser.addoption("--no", dest="no", action="store_true")
        option = parser.parse([])
        assert option.hello == "world"
        assert option.this == 42
        assert option.no is False

    def test_drop_short_helper(self):
        parser = argparse.ArgumentParser(
            formatter_class=parseopt.DropShorterLongHelpFormatter
        )
        parser.add_argument(
            "-t", "--twoword", "--duo", "--two-word", "--two", help="foo"
        ).map_long_option = {"two": "two-word"}
        # throws error on --deux only!
        parser.add_argument(
            "-d", "--deuxmots", "--deux-mots", action="store_true", help="foo"
        ).map_long_option = {"deux": "deux-mots"}
        parser.add_argument("-s", action="store_true", help="single short")
        parser.add_argument("--abc", "-a", action="store_true", help="bar")
        parser.add_argument("--klm", "-k", "--kl-m", action="store_true", help="bar")
        parser.add_argument(
            "-P", "--pq-r", "-p", "--pqr", action="store_true", help="bar"
        )
        parser.add_argument(
            "--zwei-wort", "--zweiwort", "--zweiwort", action="store_true", help="bar"
        )
        parser.add_argument(
            "-x", "--exit-on-first", "--exitfirst", action="store_true", help="spam"
        ).map_long_option = {"exitfirst": "exit-on-first"}
        parser.add_argument("files_and_dirs", nargs="*")
        args = parser.parse_args(["-k", "--duo", "hallo", "--exitfirst"])
        assert args.twoword == "hallo"
        assert args.klm is True
        assert args.zwei_wort is False
        assert args.exit_on_first is True
        assert args.s is False
        args = parser.parse_args(["--deux-mots"])
        with pytest.raises(AttributeError):
            assert args.deux_mots is True
        assert args.deuxmots is True
        args = parser.parse_args(["file", "dir"])
        assert "|".join(args.files_and_dirs) == "file|dir"

    def test_drop_short_0(self, parser):
        parser.addoption("--funcarg", "--func-arg", action="store_true")
        parser.addoption("--abc-def", "--abc-def", action="store_true")
        parser.addoption("--klm-hij", action="store_true")
        args = parser.parse(["--funcarg", "--k"])
        assert args.funcarg is True
        assert args.abc_def is False
        assert args.klm_hij is True

    def test_drop_short_2(self, parser):
        parser.addoption("--func-arg", "--doit", action="store_true")
        args = parser.parse(["--doit"])
        assert args.func_arg is True

    def test_drop_short_3(self, parser):
        """
        Test the behavior of the parser when a short option is provided without a corresponding argument.
        
        This function tests the parser's handling of a short option (`-3`) that is provided without an argument. The parser should interpret this as a boolean flag set to `False` and should also handle the remaining arguments as a list.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser instance to be tested.
        
        Returns:
        None: This function asserts the expected behavior of the parser and does not return any
        """

        parser.addoption("--func-arg", "--funcarg", "--doit", action="store_true")
        args = parser.parse(["abcd"])
        assert args.func_arg is False
        assert args.file_or_dir == ["abcd"]

    def test_drop_short_help0(self, parser, capsys):
        parser.addoption("--func-args", "--doit", help="foo", action="store_true")
        parser.parse([])
        help = parser.optparser.format_help()
        assert "--func-args, --doit  foo" in help

    # testing would be more helpful with all help generated
    def test_drop_short_help1(self, parser, capsys):
        group = parser.getgroup("general")
        group.addoption("--doit", "--func-args", action="store_true", help="foo")
        group._addoption(
            "-h",
            "--help",
            action="store_true",
            dest="help",
            help="show help message and configuration info",
        )
        parser.parse(["-h"])
        help = parser.optparser.format_help()
        assert "-doit, --func-args  foo" in help

    def test_multiple_metavar_help(self, parser):
        """
        Help text for options with a metavar tuple should display help
        in the form "--preferences=value1 value2 value3" (#2004).
        """
        group = parser.getgroup("general")
        group.addoption(
            "--preferences", metavar=("value1", "value2", "value3"), nargs=3
        )
        group._addoption("-h", "--help", action="store_true", dest="help")
        parser.parse(["-h"])
        help = parser.optparser.format_help()
        assert "--preferences=value1 value2 value3" in help


def test_argcomplete(testdir, monkeypatch):
    """
    Tests the argcomplete functionality for the pytest command.
    
    This function checks if argcomplete is available and if it can correctly complete the pytest command. It sets up a temporary bash script to run pytest with argcomplete enabled. The function uses environment variables to simulate the completion process and checks the output to ensure that the correct options and directories are being completed.
    
    Key Parameters:
    - `testdir`: The pytest test directory object used to create and run tests.
    - `monkeypatch`: A fixture from pytest used to
    """

    if not distutils.spawn.find_executable("bash"):
        pytest.skip("bash not available")
    script = str(testdir.tmpdir.join("test_argcomplete"))

    with open(str(script), "w") as fp:
        # redirect output from argcomplete to stdin and stderr is not trivial
        # http://stackoverflow.com/q/12589419/1307905
        # so we use bash
        fp.write('COMP_WORDBREAKS="$COMP_WORDBREAKS" python -m pytest 8>&1 9>&2')
    # alternative would be exteneded Testdir.{run(),_run(),popen()} to be able
    # to handle a keyword argument env that replaces os.environ in popen or
    # extends the copy, advantage: could not forget to restore
    monkeypatch.setenv("_ARGCOMPLETE", "1")
    monkeypatch.setenv("_ARGCOMPLETE_IFS", "\x0b")
    monkeypatch.setenv("COMP_WORDBREAKS", " \\t\\n\"\\'><=;|&(:")

    arg = "--fu"
    monkeypatch.setenv("COMP_LINE", "pytest " + arg)
    monkeypatch.setenv("COMP_POINT", str(len("pytest " + arg)))
    result = testdir.run("bash", str(script), arg)
    if result.ret == 255:
        # argcomplete not found
        pytest.skip("argcomplete not available")
    elif not result.stdout.str():
        pytest.skip(
            "bash provided no output on stdout, argcomplete not available? (stderr={!r})".format(
                result.stderr.str()
            )
        )
    else:
        result.stdout.fnmatch_lines(["--funcargs", "--fulltrace"])
    os.mkdir("test_argcomplete.d")
    arg = "test_argc"
    monkeypatch.setenv("COMP_LINE", "pytest " + arg)
    monkeypatch.setenv("COMP_POINT", str(len("pytest " + arg)))
    result = testdir.run("bash", str(script), arg)
    result.stdout.fnmatch_lines(["test_argcomplete", "test_argcomplete.d/"])
