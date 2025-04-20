import os

import pytest

from xarray import DataArray, tutorial

from . import assert_identical, network


@network
class TestLoadDataset:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.testfile = "tiny"

    def test_download_from_github(self, tmp_path, monkeypatch):
        """
        Download a dataset from GitHub and verify its contents.
        
        This function tests the ability to download a dataset from GitHub and
        verify its contents by comparing it with a smaller dataset.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path where the cache is stored.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment during testing.
        
        Returns:
        None: The function asserts that the downloaded dataset is identical to a smaller dataset.
        
        Notes:
        - The environment variable "
        """

        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds = tutorial.open_dataset(self.testfile).load()
        tiny = DataArray(range(5), name="tiny").to_dataset()
        assert_identical(ds, tiny)

    def test_download_from_github_load_without_cache(self, tmp_path, monkeypatch):
        """
        Test downloading and loading a dataset from GitHub without using cache.
        
        This test function checks the behavior of loading a dataset from GitHub without using the cache and compares it with the behavior when using the cache. The test uses a temporary cache directory to ensure that no external cache is used.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary path object used to set the XDG_CACHE_DIR environment variable.
        monkeypatch (pytest.MonkeyPatch): A pytest fixture used to modify the environment temporarily.
        
        Returns
        """

        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset(self.testfile, cache=False).load()
        ds_cache = tutorial.open_dataset(self.testfile).load()
        assert_identical(ds_cache, ds_nocache)

    def test_download_rasterio_from_github_load_without_cache(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset("RGB.byte", cache=False).load()
        ds_cache = tutorial.open_dataset("RGB.byte", cache=True).load()
        assert_identical(ds_cache, ds_nocache)
