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
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds = tutorial.open_dataset(self.testfile).load()
        tiny = DataArray(range(5), name="tiny").to_dataset()
        assert_identical(ds, tiny)

    def test_download_from_github_load_without_cache(self, tmp_path, monkeypatch):
        """
        Tests the functionality of downloading and loading a dataset from GitHub without using cache.
        
        This test ensures that the dataset can be loaded both with and without cache, and that the resulting datasets are identical.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment during the test.
        
        Returns:
        None: This function does not return any value. It asserts that the datasets loaded with and without cache are
        """

        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset(self.testfile, cache=False).load()
        ds_cache = tutorial.open_dataset(self.testfile).load()
        assert_identical(ds_cache, ds_nocache)

    def test_download_rasterio_from_github_load_without_cache(
        """
        Download and load a raster dataset from GitHub using Rasterio without caching and with caching. The function compares the datasets loaded with and without caching to ensure they are identical.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment temporarily.
        
        Returns:
        None: The function asserts that the datasets loaded with and without caching are identical.
        
        Key Steps:
        1. Set the environment variable `X
        """

        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset("RGB.byte", cache=False).load()
        ds_cache = tutorial.open_dataset("RGB.byte", cache=True).load()
        assert_identical(ds_cache, ds_nocache)
