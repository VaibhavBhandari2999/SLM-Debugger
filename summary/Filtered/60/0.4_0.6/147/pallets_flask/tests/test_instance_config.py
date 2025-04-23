import os
import sys

import pytest

import flask


def test_explicit_instance_paths(modules_tmpdir):
    with pytest.raises(ValueError) as excinfo:
        flask.Flask(__name__, instance_path="instance")
    assert "must be absolute" in str(excinfo.value)

    app = flask.Flask(__name__, instance_path=str(modules_tmpdir))
    assert app.instance_path == str(modules_tmpdir)


@pytest.mark.xfail(reason="weird interaction with tox")
def test_main_module_paths(modules_tmpdir, purge_module):
    """
    Test the main module paths for a Flask application.
    
    This function checks the instance path of a Flask application defined in a main module. The module is assumed to be located in a temporary directory and is purged after the test.
    
    Parameters:
    modules_tmpdir (pathlib.Path): A temporary directory path where the main module is located.
    purge_module (function): A function to purge the module after the test.
    
    Returns:
    None: This function does not return any value. It asserts the correctness
    """

    app = modules_tmpdir.join("main_app.py")
    app.write('import flask\n\napp = flask.Flask("__main__")')
    purge_module("main_app")

    from main_app import app

    here = os.path.abspath(os.getcwd())
    assert app.instance_path == os.path.join(here, "instance")


@pytest.mark.xfail(reason="weird interaction with tox")
def test_uninstalled_module_paths(modules_tmpdir, purge_module):
    """
    Test the behavior of a Flask application when a required module is uninstalled.
    
    This function checks that the Flask application correctly handles the absence of a required module by setting the instance path to a default location.
    
    Parameters:
    - modules_tmpdir (LocalPath): A temporary directory used to store the module files.
    - purge_module (Callable): A function to uninstall the specified module.
    
    The function imports the Flask application from the specified module and verifies that the instance path is set to the expected default location.
    
    Returns:
    """

    app = modules_tmpdir.join("config_module_app.py").write(
        "import os\n"
        "import flask\n"
        "here = os.path.abspath(os.path.dirname(__file__))\n"
        "app = flask.Flask(__name__)\n"
    )
    purge_module("config_module_app")

    from config_module_app import app

    assert app.instance_path == str(modules_tmpdir.join("instance"))


@pytest.mark.xfail(reason="weird interaction with tox")
def test_uninstalled_package_paths(modules_tmpdir, purge_module):
    app = modules_tmpdir.mkdir("config_package_app")
    init = app.join("__init__.py")
    init.write(
        "import os\n"
        "import flask\n"
        "here = os.path.abspath(os.path.dirname(__file__))\n"
        "app = flask.Flask(__name__)\n"
    )
    purge_module("config_package_app")

    from config_package_app import app

    assert app.instance_path == str(modules_tmpdir.join("instance"))


def test_installed_module_paths(
    modules_tmpdir, modules_tmpdir_prefix, purge_module, site_packages, limit_loader
):
    site_packages.join("site_app.py").write(
        "import flask\napp = flask.Flask(__name__)\n"
    )
    purge_module("site_app")

    from site_app import app

    assert app.instance_path == modules_tmpdir.join("var").join("site_app-instance")


def test_installed_package_paths(
    limit_loader, modules_tmpdir, modules_tmpdir_prefix, purge_module, monkeypatch
):
    installed_path = modules_tmpdir.mkdir("path")
    monkeypatch.syspath_prepend(installed_path)

    app = installed_path.mkdir("installed_package")
    init = app.join("__init__.py")
    init.write("import flask\napp = flask.Flask(__name__)")
    purge_module("installed_package")

    from installed_package import app

    assert app.instance_path == modules_tmpdir.join("var").join(
        "installed_package-instance"
    )


def test_prefix_package_paths(
    limit_loader, modules_tmpdir, modules_tmpdir_prefix, purge_module, site_packages
):
    app = site_packages.mkdir("site_package")
    init = app.join("__init__.py")
    init.write("import flask\napp = flask.Flask(__name__)")
    purge_module("site_package")

    import site_package

    assert site_package.app.instance_path == modules_tmpdir.join("var").join(
        "site_package-instance"
    )


def test_egg_installed_paths(install_egg, modules_tmpdir, modules_tmpdir_prefix):
    """
    Tests the installation of an egg and checks if the correct paths are set for the installed modules.
    
    This function installs an egg in a specified directory and then imports the installed module to verify that the instance path is correctly set.
    
    Parameters:
    install_egg (function): A function that installs an egg in the specified directory.
    modules_tmpdir (pathlib.Path): The temporary directory where the egg is installed.
    modules_tmpdir_prefix (str): The prefix for the temporary directory.
    
    Returns:
    """

    modules_tmpdir.mkdir("site_egg").join("__init__.py").write(
        "import flask\n\napp = flask.Flask(__name__)"
    )
    install_egg("site_egg")
    try:
        import site_egg

        assert site_egg.app.instance_path == str(
            modules_tmpdir.join("var/").join("site_egg-instance")
        )
    finally:
        if "site_egg" in sys.modules:
            del sys.modules["site_egg"]
modules["site_egg"]
