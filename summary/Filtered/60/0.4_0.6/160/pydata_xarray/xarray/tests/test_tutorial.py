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
        Tests downloading a dataset from GitHub.
        
        This function tests the ability to download a dataset from GitHub using a temporary cache directory. It sets the environment variable `XDG_CACHE_DIR` to the provided temporary path and then loads a dataset from a test file. The function compares the loaded dataset with a tiny dataset to ensure they are identical.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching downloaded files.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify
        """

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
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("XDG_CACHE_DIR", os.fspath(tmp_path))

        ds_nocache = tutorial.open_dataset("RGB.byte", cache=False).load()
        ds_cache = tutorial.open_dataset("RGB.byte", cache=True).load()
        assert_identical(ds_cache, ds_nocache)
