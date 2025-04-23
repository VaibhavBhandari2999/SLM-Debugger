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
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset(self.testfile, cache=False).load()
        ds_cache = tutorial.open_dataset(self.testfile).load()
        assert_identical(ds_cache, ds_nocache)

    def test_download_rasterio_from_github_load_without_cache(
        """
        Test downloading and loading a rasterio dataset from GitHub without using the cache.
        
        This test function checks that a rasterio dataset can be downloaded and loaded from GitHub without using the cache, and that the result is identical to when the cache is used.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching.
        monkeypatch (pytest.MonkeyPatch): A pytest fixture for modifying the environment during the test.
        
        Returns:
        None: This function does not return any value.
        """

        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset("RGB.byte", cache=False).load()
        ds_cache = tutorial.open_dataset("RGB.byte", cache=True).load()
        assert_identical(ds_cache, ds_nocache)
