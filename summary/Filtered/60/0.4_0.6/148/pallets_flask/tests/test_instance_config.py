import sys

import pytest

import flask


def test_explicit_instance_paths(modules_tmpdir):
    """
    This function tests the behavior of the Flask application instance path.
    
    Parameters:
    - modules_tmpdir (pathlib.Path): A temporary directory path for the Flask instance.
    
    Returns:
    - None: The function asserts the correct behavior by raising a ValueError if the instance path is not absolute and checks if the instance path is set correctly.
    
    Raises:
    - ValueError: If the provided instance path is not an absolute path.
    """

    with pytest.raises(ValueError) as excinfo:
        flask.Flask(__name__, instance_path="instance")
    assert "must be absolute" in str(excinfo.value)

    app = flask.Flask(__name__, instance_path=str(modules_tmpdir))
    assert app.instance_path == str(modules_tmpdir)


def test_uninstalled_module_paths(modules_tmpdir, purge_module):
    app = modules_tmpdir.join("config_module_app.py").write(
        "import os\n"
        "import flask\n"
        "here = os.path.abspath(os.path.dirname(__file__))\n"
        "app = flask.Flask(__name__)\n"
    )
    purge_module("config_module_app")

    from config_module_app import app

    assert app.instance_path == str(modules_tmpdir.join("instance"))


def test_uninstalled_package_paths(modules_tmpdir, purge_module):
    """
    Test the paths of an uninstalled package in a Flask application.
    
    This function checks the instance path of a Flask application when the package is uninstalled.
    
    Parameters:
    - modules_tmpdir (pathlib.Path): The temporary directory where the module is located.
    - purge_module (function): A function to uninstall the module.
    
    Returns:
    - None: This function asserts the correctness of the instance path and does not return any value.
    """

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


def test_uninstalled_namespace_paths(tmpdir, monkeypatch, purge_module):
    def create_namespace(package):
        project = tmpdir.join(f"project-{package}")
        monkeypatch.syspath_prepend(str(project))
        project.join("namespace").join(package).join("__init__.py").write(
            "import flask\napp = flask.Flask(__name__)\n", ensure=True
        )
        return project

    _ = create_namespace("package1")
    project2 = create_namespace("package2")
    purge_module("namespace.package2")
    purge_module("namespace")

    from namespace.package2 import app

    assert app.instance_path == str(project2.join("instance"))


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
-instance")
        )
    finally:
        if "site_egg" in sys.modules:
            del sys.modules["site_egg"]
