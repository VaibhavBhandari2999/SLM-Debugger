from setuptools import setup

# TODO: if py gets upgrade to >=1.6,
#       remove _width_of_current_line in terminal.py
INSTALL_REQUIRES = [
    "py>=1.5.0",
    "packaging",
    "attrs>=17.4.0",
    "more-itertools>=4.0.0",
    "atomicwrites>=1.0",
    'pathlib2>=2.2.0;python_version<"3.6"',
    'colorama;sys_platform=="win32"',
    "pluggy>=0.12,<1.0",
    'importlib-metadata>=0.12;python_version<"3.8"',
    "wcwidth",
]


def main():
    """
    Generate a setup configuration for a Python package.
    
    This function configures the setup for a Python package, including versioning, dependencies, and package directory.
    
    Parameters:
    use_scm_version (dict): A dictionary specifying the versioning configuration. It includes the method to write the version to a file.
    setup_requires (list): A list of packages required for setup.
    package_dir (dict): A dictionary specifying the package directory structure.
    extras_require (dict): A dictionary specifying additional dependencies for
    """

    setup(
        use_scm_version={"write_to": "src/_pytest/_version.py"},
        setup_requires=["setuptools-scm", "setuptools>=40.0"],
        package_dir={"": "src"},
        # fmt: off
        extras_require={
            "testing": [
                "argcomplete",
                "hypothesis>=3.56",
                "mock",
                "nose",
                "requests",
            ],
        },
        # fmt: on
        install_requires=INSTALL_REQUIRES,
    )


if __name__ == "__main__":
    main()
