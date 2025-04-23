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
        Test downloading a dataset from GitHub.
        
        This test sets the environment variable `XDG_CACHE_DIR` to a temporary path and then loads a dataset from a test file using `tutorial.open_dataset`. It compares the loaded dataset `ds` with a small dataset `tiny` to ensure they are identical.
        
        Parameters:
        tmp_path (pathlib.Path): A temporary directory path used for caching.
        monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment during testing.
        
        Returns:
        None
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
