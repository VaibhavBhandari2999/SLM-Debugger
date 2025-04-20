import os

import numpy as np
import pandas as pd

import xarray as xr

from . import randint, randn, requires_dask

try:
    import dask
    import dask.multiprocessing
except ImportError:
    pass


os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"


class IOSingleNetCDF:
    """
    A few examples that benchmark reading/writing a single netCDF file with
    xarray
    """

    timeout = 300.0
    repeat = 1
    number = 5

    def make_ds(self):

        # single Dataset
        self.ds = xr.Dataset()
        self.nt = 1000
        self.nx = 90
        self.ny = 45

        self.block_chunks = {
            "time": self.nt / 4,
            "lon": self.nx / 3,
            "lat": self.ny / 3,
        }

        self.time_chunks = {"time": int(self.nt / 36)}

        times = pd.date_range("1970-01-01", periods=self.nt, freq="D")
        lons = xr.DataArray(
            np.linspace(0, 360, self.nx),
            dims=("lon",),
            attrs={"units": "degrees east", "long_name": "longitude"},
        )
        lats = xr.DataArray(
            np.linspace(-90, 90, self.ny),
            dims=("lat",),
            attrs={"units": "degrees north", "long_name": "latitude"},
        )
        self.ds["foo"] = xr.DataArray(
            randn((self.nt, self.nx, self.ny), frac_nan=0.2),
            coords={"lon": lons, "lat": lats, "time": times},
            dims=("time", "lon", "lat"),
            name="foo",
            encoding=None,
            attrs={"units": "foo units", "description": "a description"},
        )
        self.ds["bar"] = xr.DataArray(
            randn((self.nt, self.nx, self.ny), frac_nan=0.2),
            coords={"lon": lons, "lat": lats, "time": times},
            dims=("time", "lon", "lat"),
            name="bar",
            encoding=None,
            attrs={"units": "bar units", "description": "a description"},
        )
        self.ds["baz"] = xr.DataArray(
            randn((self.nx, self.ny), frac_nan=0.2).astype(np.float32),
            coords={"lon": lons, "lat": lats},
            dims=("lon", "lat"),
            name="baz",
            encoding=None,
            attrs={"units": "baz units", "description": "a description"},
        )

        self.ds.attrs = {"history": "created for xarray benchmarking"}

        self.oinds = {
            "time": randint(0, self.nt, 120),
            "lon": randint(0, self.nx, 20),
            "lat": randint(0, self.ny, 10),
        }
        self.vinds = {
            "time": xr.DataArray(randint(0, self.nt, 120), dims="x"),
            "lon": xr.DataArray(randint(0, self.nx, 120), dims="x"),
            "lat": slice(3, 20),
        }


class IOWriteSingleNetCDF3(IOSingleNetCDF):
    def setup(self):
        self.format = "NETCDF3_64BIT"
        self.make_ds()

    def time_write_dataset_netcdf4(self):
        self.ds.to_netcdf("test_netcdf4_write.nc", engine="netcdf4", format=self.format)

    def time_write_dataset_scipy(self):
        self.ds.to_netcdf("test_scipy_write.nc", engine="scipy", format=self.format)


class IOReadSingleNetCDF4(IOSingleNetCDF):
    def setup(self):
        """
        Setup function for creating a NetCDF file.
        
        This function initializes the dataset, sets the file path and format, and saves the dataset to a NetCDF file.
        
        Parameters:
        self (object): The object instance containing the dataset and other attributes.
        
        Returns:
        None: This function does not return any value. It saves the dataset to a file.
        
        Attributes used:
        - self.make_ds(): A method to create the dataset.
        - self.filepath (str): The path to save the Net
        """


        self.make_ds()

        self.filepath = "test_single_file.nc4.nc"
        self.format = "NETCDF4"
        self.ds.to_netcdf(self.filepath, format=self.format)

    def time_load_dataset_netcdf4(self):
        xr.open_dataset(self.filepath, engine="netcdf4").load()

    def time_orthogonal_indexing(self):
        ds = xr.open_dataset(self.filepath, engine="netcdf4")
        ds = ds.isel(**self.oinds).load()

    def time_vectorized_indexing(self):
        ds = xr.open_dataset(self.filepath, engine="netcdf4")
        ds = ds.isel(**self.vinds).load()


class IOReadSingleNetCDF3(IOReadSingleNetCDF4):
    def setup(self):

        self.make_ds()

        self.filepath = "test_single_file.nc3.nc"
        self.format = "NETCDF3_64BIT"
        self.ds.to_netcdf(self.filepath, format=self.format)

    def time_load_dataset_scipy(self):
        xr.open_dataset(self.filepath, engine="scipy").load()

    def time_orthogonal_indexing(self):
        ds = xr.open_dataset(self.filepath, engine="scipy")
        ds = ds.isel(**self.oinds).load()

    def time_vectorized_indexing(self):
        ds = xr.open_dataset(self.filepath, engine="scipy")
        ds = ds.isel(**self.vinds).load()


class IOReadSingleNetCDF4Dask(IOSingleNetCDF):
    def setup(self):
        """
        Setup method for creating a NetCDF file.
        
        This method sets up a Dask-based data structure and writes it to a NetCDF file.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Ensures that Dask is available.
        2. Calls the `make_ds` method to create a Dask-backed dataset.
        3. Specifies the file path and format for the NetCDF file.
        4. Writes the dataset to the specified NetCDF file using the specified format.
        
        Notes:
        """


        requires_dask()

        self.make_ds()

        self.filepath = "test_single_file.nc4.nc"
        self.format = "NETCDF4"
        self.ds.to_netcdf(self.filepath, format=self.format)

    def time_load_dataset_netcdf4_with_block_chunks(self):
        xr.open_dataset(
            self.filepath, engine="netcdf4", chunks=self.block_chunks
        ).load()

    def time_load_dataset_netcdf4_with_block_chunks_oindexing(self):
        ds = xr.open_dataset(self.filepath, engine="netcdf4", chunks=self.block_chunks)
        ds = ds.isel(**self.oinds).load()

    def time_load_dataset_netcdf4_with_block_chunks_vindexing(self):
        ds = xr.open_dataset(self.filepath, engine="netcdf4", chunks=self.block_chunks)
        ds = ds.isel(**self.vinds).load()

    def time_load_dataset_netcdf4_with_block_chunks_multiprocessing(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_dataset(
                self.filepath, engine="netcdf4", chunks=self.block_chunks
            ).load()

    def time_load_dataset_netcdf4_with_time_chunks(self):
        xr.open_dataset(self.filepath, engine="netcdf4", chunks=self.time_chunks).load()

    def time_load_dataset_netcdf4_with_time_chunks_multiprocessing(self):
        """
        Loads a NetCDF4 dataset using Dask and multiprocessing for parallel processing. The dataset is chunked along the time dimension for efficient memory management.
        
        Parameters:
        self (object): The object instance that contains the `filepath` and `time_chunks` attributes.
        
        Attributes:
        filepath (str): The path to the NetCDF4 file to be loaded.
        time_chunks (dict): A dictionary specifying the chunk size for the time dimension.
        
        Returns:
        xarray.Dataset: The loaded NetCDF4
        """

        with dask.config.set(scheduler="multiprocessing"):
            xr.open_dataset(
                self.filepath, engine="netcdf4", chunks=self.time_chunks
            ).load()


class IOReadSingleNetCDF3Dask(IOReadSingleNetCDF4Dask):
    def setup(self):
        """
        Setup function for creating a NetCDF file.
        
        This function sets up a Dask-based data structure, creates a NetCDF file, and saves the data to the specified file path.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Ensures that Dask is available.
        2. Calls the `make_ds` method to create a Dask-based data structure.
        3. Sets the file path and format for the NetCDF file.
        4. Saves the Dask-based data structure
        """


        requires_dask()

        self.make_ds()

        self.filepath = "test_single_file.nc3.nc"
        self.format = "NETCDF3_64BIT"
        self.ds.to_netcdf(self.filepath, format=self.format)

    def time_load_dataset_scipy_with_block_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_dataset(
                self.filepath, engine="scipy", chunks=self.block_chunks
            ).load()

    def time_load_dataset_scipy_with_block_chunks_oindexing(self):
        ds = xr.open_dataset(self.filepath, engine="scipy", chunks=self.block_chunks)
        ds = ds.isel(**self.oinds).load()

    def time_load_dataset_scipy_with_block_chunks_vindexing(self):
        ds = xr.open_dataset(self.filepath, engine="scipy", chunks=self.block_chunks)
        ds = ds.isel(**self.vinds).load()

    def time_load_dataset_scipy_with_time_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_dataset(
                self.filepath, engine="scipy", chunks=self.time_chunks
            ).load()


class IOMultipleNetCDF:
    """
    A few examples that benchmark reading/writing multiple netCDF files with
    xarray
    """

    timeout = 300.0
    repeat = 1
    number = 5

    def make_ds(self, nfiles=10):

        # multiple Dataset
        self.ds = xr.Dataset()
        self.nt = 1000
        self.nx = 90
        self.ny = 45
        self.nfiles = nfiles

        self.block_chunks = {
            "time": self.nt / 4,
            "lon": self.nx / 3,
            "lat": self.ny / 3,
        }

        self.time_chunks = {"time": int(self.nt / 36)}

        self.time_vars = np.split(
            pd.date_range("1970-01-01", periods=self.nt, freq="D"), self.nfiles
        )

        self.ds_list = []
        self.filenames_list = []
        for i, times in enumerate(self.time_vars):
            ds = xr.Dataset()
            nt = len(times)
            lons = xr.DataArray(
                np.linspace(0, 360, self.nx),
                dims=("lon",),
                attrs={"units": "degrees east", "long_name": "longitude"},
            )
            lats = xr.DataArray(
                np.linspace(-90, 90, self.ny),
                dims=("lat",),
                attrs={"units": "degrees north", "long_name": "latitude"},
            )
            ds["foo"] = xr.DataArray(
                randn((nt, self.nx, self.ny), frac_nan=0.2),
                coords={"lon": lons, "lat": lats, "time": times},
                dims=("time", "lon", "lat"),
                name="foo",
                encoding=None,
                attrs={"units": "foo units", "description": "a description"},
            )
            ds["bar"] = xr.DataArray(
                randn((nt, self.nx, self.ny), frac_nan=0.2),
                coords={"lon": lons, "lat": lats, "time": times},
                dims=("time", "lon", "lat"),
                name="bar",
                encoding=None,
                attrs={"units": "bar units", "description": "a description"},
            )
            ds["baz"] = xr.DataArray(
                randn((self.nx, self.ny), frac_nan=0.2).astype(np.float32),
                coords={"lon": lons, "lat": lats},
                dims=("lon", "lat"),
                name="baz",
                encoding=None,
                attrs={"units": "baz units", "description": "a description"},
            )

            ds.attrs = {"history": "created for xarray benchmarking"}

            self.ds_list.append(ds)
            self.filenames_list.append("test_netcdf_%i.nc" % i)


class IOWriteMultipleNetCDF3(IOMultipleNetCDF):
    def setup(self):
        self.make_ds()
        self.format = "NETCDF3_64BIT"

    def time_write_dataset_netcdf4(self):
        """
        Save a list of xarray datasets to a list of netCDF4 files.
        
        Parameters:
        ds_list (list): A list of xarray.Dataset objects to be saved.
        filenames_list (list): A list of filenames to which the datasets will be saved.
        engine (str, optional): The engine to use for saving the datasets. Defaults to 'netcdf4'.
        format (str, optional): The format of the output files. Defaults to the format specified in the class instance.
        """

        xr.save_mfdataset(
            self.ds_list, self.filenames_list, engine="netcdf4", format=self.format
        )

    def time_write_dataset_scipy(self):
        xr.save_mfdataset(
            self.ds_list, self.filenames_list, engine="scipy", format=self.format
        )


class IOReadMultipleNetCDF4(IOMultipleNetCDF):
    def setup(self):

        requires_dask()

        self.make_ds()
        self.format = "NETCDF4"
        xr.save_mfdataset(self.ds_list, self.filenames_list, format=self.format)

    def time_load_dataset_netcdf4(self):
        xr.open_mfdataset(self.filenames_list, engine="netcdf4").load()

    def time_open_dataset_netcdf4(self):
        xr.open_mfdataset(self.filenames_list, engine="netcdf4")


class IOReadMultipleNetCDF3(IOReadMultipleNetCDF4):
    def setup(self):
        """
        Setup function for saving multiple datasets to NetCDF files.
        
        This function sets up the environment and saves a list of xarray datasets to multiple NetCDF files.
        
        Parameters:
        self (object): The object instance containing the necessary attributes and methods.
        
        Key Parameters:
        ds_list (list): A list of xarray datasets to be saved.
        filenames_list (list): A list of filenames to save the datasets to.
        
        Keywords:
        format (str, optional): The format of the NetCDF files.
        """


        requires_dask()

        self.make_ds()
        self.format = "NETCDF3_64BIT"
        xr.save_mfdataset(self.ds_list, self.filenames_list, format=self.format)

    def time_load_dataset_scipy(self):
        xr.open_mfdataset(self.filenames_list, engine="scipy").load()

    def time_open_dataset_scipy(self):
        xr.open_mfdataset(self.filenames_list, engine="scipy")


class IOReadMultipleNetCDF4Dask(IOMultipleNetCDF):
    def setup(self):

        requires_dask()

        self.make_ds()
        self.format = "NETCDF4"
        xr.save_mfdataset(self.ds_list, self.filenames_list, format=self.format)

    def time_load_dataset_netcdf4_with_block_chunks(self):
        xr.open_mfdataset(
            self.filenames_list, engine="netcdf4", chunks=self.block_chunks
        ).load()

    def time_load_dataset_netcdf4_with_block_chunks_multiprocessing(self):
        """
        Load a dataset from multiple NetCDF4 files using Dask with multiprocessing and block chunks.
        
        This function loads multiple NetCDF4 files into a Dask dataset, utilizing multiprocessing for parallel processing and block chunks for efficient memory management.
        
        Parameters:
        filenames_list (list): A list of file paths to the NetCDF4 files to be loaded.
        block_chunks (dict): A dictionary specifying the chunk size for each dimension in the Dask dataset.
        
        Returns:
        xarray.Dataset: A Dask-backed
        """

        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="netcdf4", chunks=self.block_chunks
            ).load()

    def time_load_dataset_netcdf4_with_time_chunks(self):
        xr.open_mfdataset(
            self.filenames_list, engine="netcdf4", chunks=self.time_chunks
        ).load()

    def time_load_dataset_netcdf4_with_time_chunks_multiprocessing(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="netcdf4", chunks=self.time_chunks
            ).load()

    def time_open_dataset_netcdf4_with_block_chunks(self):
        xr.open_mfdataset(
            self.filenames_list, engine="netcdf4", chunks=self.block_chunks
        )

    def time_open_dataset_netcdf4_with_block_chunks_multiprocessing(self):
        """
        Open multiple NetCDF4 datasets in parallel using Dask and multiprocessing.
        
        This function opens a list of NetCDF4 files using Dask's `open_mfdataset` with the `netcdf4` engine. It utilizes multiprocessing to handle the opening and chunking of the datasets in parallel.
        
        Parameters:
        filenames_list (list): A list of file paths to the NetCDF4 files to be opened.
        block_chunks (dict): A dictionary specifying the chunk size for each dimension in the datasets
        """

        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="netcdf4", chunks=self.block_chunks
            )

    def time_open_dataset_netcdf4_with_time_chunks(self):
        """
        Open multiple NetCDF4 files as a single xarray dataset with time dimension chunking.
        
        Parameters:
        filenames_list (list): List of file paths to NetCDF4 files.
        time_chunks (int): Size of chunks for the time dimension.
        
        Returns:
        xarray.Dataset: An xarray dataset containing the concatenated data from the specified NetCDF4 files.
        
        Notes:
        This function uses the 'netcdf4' engine to open the files and applies chunking specifically to the time dimension for
        """

        xr.open_mfdataset(
            self.filenames_list, engine="netcdf4", chunks=self.time_chunks
        )

    def time_open_dataset_netcdf4_with_time_chunks_multiprocessing(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="netcdf4", chunks=self.time_chunks
            )


class IOReadMultipleNetCDF3Dask(IOReadMultipleNetCDF4Dask):
    def setup(self):

        requires_dask()

        self.make_ds()
        self.format = "NETCDF3_64BIT"
        xr.save_mfdataset(self.ds_list, self.filenames_list, format=self.format)

    def time_load_dataset_scipy_with_block_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="scipy", chunks=self.blhunks
            ).load()

    def time_load_dataset_scipy_with_time_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="scipy", chunks=self.time_chunks
            ).load()

    def time_open_dataset_scipy_with_block_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="scipy", chunks=self.block_chunks
            )

    def time_open_dataset_scipy_with_time_chunks(self):
        with dask.config.set(scheduler="multiprocessing"):
            xr.open_mfdataset(
                self.filenames_list, engine="scipy", chunks=self.time_chunks
            )


def create_delayed_write():
    import dask.array as da

    vals = da.random.random(300, chunks=(1,))
    ds = xr.Dataset({"vals": (["a"], vals)})
    return ds.to_netcdf("file.nc", engine="netcdf4", compute=False)


class IOWriteNetCDFDask:
    timeout = 60
    repeat = 1
    number = 5

    def setup(self):
        requires_dask()
        self.write = create_delayed_write()

    def time_write(self):
        self.write.compute()


class IOWriteNetCDFDaskDistributed:
    def setup(self):
        try:
            import distributed
        except ImportError:
            raise NotImplementedError()
        self.client = distributed.Client()
        self.write = create_delayed_write()

    def cleanup(self):
        self.client.shutdown()

    def time_write(self):
        self.write.compute()
te()
.write.compute()
te()
