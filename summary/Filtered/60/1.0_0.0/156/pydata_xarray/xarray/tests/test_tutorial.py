import os
from contextlib import suppress

import pytest

from xarray import DataArray, tutorial

from . import assert_identical, network


@network
class TestLoadDataset:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.testfile = "tiny"
        self.testfilepath = os.path.expanduser(
            os.sep.join(("~", ".xarray_tutorial_data", self.testfile))
        )
        with suppress(OSError):
            os.remove("{}.nc".format(self.testfilepath))
        with suppress(OSError):
            os.remove("{}.md5".format(self.testfilepath))

    def test_download_from_github(self):
        """
        Test downloading and loading a dataset from a GitHub file.
        
        This function loads a dataset from a specified test file and compares it to a tiny dataset. The test checks if the loaded dataset is identical to the tiny dataset.
        
        Parameters:
        testfile (str): The path to the test file to be loaded.
        
        Returns:
        None: This function does not return any value. It asserts that the loaded dataset is identical to the tiny dataset.
        """

        ds = tutorial.open_dataset(self.testfile).load()
        tiny = DataArray(range(5), name="tiny").to_dataset()
        assert_identical(ds, tiny)

    def test_download_from_github_load_without_cache(self):
        """
        Tests the functionality of downloading and loading a dataset from GitHub without using cache.
        
        This function checks whether a dataset can be loaded from a specified file on GitHub without using cache and compares it with a cached version of the same dataset. If both versions of the dataset are identical, the test passes.
        
        Parameters:
        self (object): The test object containing the necessary attributes and methods for the test.
        
        Returns:
        None: The function asserts the equality of the two datasets and does not return any value. If
        """

        ds_nocache = tutorial.open_dataset(self.testfile, cache=False).load()
        ds_cache = tutorial.open_dataset(self.testfile).load()
        assert_identical(ds_cache, ds_nocache)
