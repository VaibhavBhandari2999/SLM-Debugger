from setuptools import setup

# TODO: if py gets upgrade to >=1.6,
#       remove _width_of_current_line in terminal.py
INSTALL_REQUIRES = [
    "py>=1.5.0",
    "packaging",
    "attrs>=17.4.0",  # should match oldattrs tox env.
    "more-itertools>=4.0.0",
    'atomicwrites>=1.0;sys_platform=="win32"',
    'pathlib2>=2.2.0;python_version<"3.6"',
    'colorama;sys_platform=="win32"',
    "pluggy>=0.12,<1.0",
    'importlib-metadata>=0.12;python_version<"3.8"',
    "wcwidth",
]


def main():
    """
    This function configures the setup for a Python package. It uses `setuptools-scm` to manage versioning and includes specific requirements for testing and quality assurance.
    
    Parameters:
    use_scm_version (dict): Configuration for versioning using `setuptools-scm`, including the path to write the version information.
    setup_requires (list): List of dependencies required for setup, including `setuptools-scm` and a minimum version of `setuptools`.
    package_dir (dict): Directory
    """

    setup(
        use_scm_version={"write_to": "src/_pytest/_version.py"},
        setup_requires=["setuptools-scm", "setuptools>=40.0"],
        package_dir={"": "src"},
        extras_require={
            "testing": [
                "argcomplete",
                "hypothesis>=3.56",
                "mock",
                "nose",
                "requests",
                "xmlschema",
            ],
            "checkqa-mypy": [
                "mypy==v0.770",  # keep this in sync with .pre-commit-config.yaml.
            ],
        },
        install_requires=INSTALL_REQUIRES,
    )


if __name__ == "__main__":
    main()
