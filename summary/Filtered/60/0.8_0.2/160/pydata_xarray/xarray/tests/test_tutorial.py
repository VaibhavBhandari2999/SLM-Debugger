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
        Tests the `download_from_github` functionality.
        
        This function tests the `download_from_github` method by setting the environment variable `XDG_CACHE_DIR` to a temporary path. It then loads a dataset from a test file and compares it to a tiny dataset to ensure they are identical.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment temporarily.
        
        Returns:
        None:
        """

        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds = tutorial.open_dataset(self.testfile).load()
        tiny = DataArray(range(5), name="tiny").to_dataset()
        assert_identical(ds, tiny)

    def test_download_from_github_load_without_cache(self, tmp_path, monkeypatch):
        """
        Tests the functionality of downloading and loading a dataset from GitHub without using cache.
        
        This function verifies that loading a dataset from a specified file without caching produces the same result as loading it with caching enabled.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for setting the XDG_CACHE_DIR environment variable.
        monkeypatch (pytest.MonkeyPatch): A fixture from pytest used to modify the environment during testing.
        
        Returns:
        None: This function does not return anything. It asserts that
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
