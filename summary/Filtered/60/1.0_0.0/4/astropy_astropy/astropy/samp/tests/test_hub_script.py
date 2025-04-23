import sys

from ..hub_script import hub_script

from .. import conf


def setup_module(module):
    conf.use_internet = False


def setup_function(function):
    function.sys_argv_orig = sys.argv
    sys.argv = ["samp_hub"]


def teardown_function(function):
    sys.argv = function.sys_argv_orig


def test_hub_script():
    """
    Runs a hub script with specific configurations.
    
    This function runs a hub script in multiple mode with web profile disabled. It sets the timeout to 3 seconds.
    
    Parameters:
    timeout (int): The duration in seconds to run the hub script before timing out. Default is 3 seconds.
    
    Note:
    - The function appends '-m' and '-w' to sys.argv to configure the script mode and web profile settings.
    - The function call to 'hub_script' is made with the specified
    """

    sys.argv.append('-m')  # run in multiple mode
    sys.argv.append('-w')  # disable web profile
    hub_script(timeout=3)
