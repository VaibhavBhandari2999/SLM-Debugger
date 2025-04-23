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
    "importlib-metadata>=0.12",
    "wcwidth",
]


def main():
    """
    Generates a setup configuration for a Python package.
    
    This function configures the setup for a Python package using setuptools. It includes the following key parameters:
    - `use_scm_version`: A dictionary specifying the versioning strategy, including writing the version to a specific file.
    - `setup_requires`: A list of packages required for setup, including `setuptools-scm` for versioning and `setuptools` with a minimum version of 40.0.
    - `package_dir`: A dictionary
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
