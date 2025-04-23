import os
from contextlib import suppress

import pytest

from xarray import DataArray, tutorial

from . import assert_identical, network


@network
class TestLoadDataset:
    @pytest.fixture(autouse=True)
    def setUp(self):
        """
        Sets up the test environment for the test file.
        
        This method initializes the test file path and ensures that any existing test files are removed. The test file is specified by the `testfile` parameter, which defaults to "tiny". The test file path is constructed using the user's home directory and the specified test file name.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - `testfile`: The name of the test file, default is "tiny".
        - The method removes any
        """

        self.testfile = "tiny"
        self.testfilepath = os.path.expanduser(
            os.sep.join(("~", ".xarray_tutorial_data", self.testfile))
        )
        with suppress(OSError):
            os.remove(f"{self.testfilepath}.nc")
        with suppress(OSError):
            os.remove(f"{self.testfilepath}.md5")

    def test_download_from_github(self):
        ds = tutorial.open_dataset(self.testfile).load()
        tiny = DataArray(range(5), name="tiny").to_dataset()
        assert_identical(ds, tiny)

    def test_download_from_github_load_without_cache(self):
        """
        Test downloading and loading a dataset from GitHub without using cache.
        
        This function tests the functionality of downloading and loading a dataset from GitHub. It ensures that the dataset is loaded without using a cache and compares it with the dataset loaded with a cache to ensure they are identical.
        
        Parameters:
        self (object): The test object instance, which contains the necessary attributes and methods for the test.
        
        Returns:
        None: This function does not return any value. It asserts the equality of two datasets.
        
        Key Steps:
        """

        ds_nocache = tutorial.open_dataset(self.testfile, cache=False).load()
        ds_cache = tutorial.open_dataset(self.testfile).load()
        assert_identical(ds_cache, ds_nocache)
