import dask.array as da

from astropy.utils.data_info import ParentDtypeInfo

__all__ = ["as_dask_column"]


class DaskInfo(ParentDtypeInfo):
    @staticmethod
    def default_format(val):
        return f"{val.compute()}"


class DaskColumn(da.Array):
    info = DaskInfo()

    def copy(self):
        # Array hard-codes the resulting copied array as Array, so need to
        # overload this since Table tries to copy the array.
        return as_dask_column(self, info=self.info)

    def __getitem__(self, item):
        result = super().__getitem__(item)
        if isinstance(item, int):
            return result
        else:
            return as_dask_column(result, info=self.info)

    def insert(self, obj, values, axis=0):
        return as_dask_column(da.insert(self, obj, values, axis=axis), info=self.info)


def as_dask_column(array, info=None):
    """
    Generate a DaskColumn from a Dask array.
    
    Parameters:
    array (dask.array.Array): The Dask array to convert into a DaskColumn.
    info (dict, optional): Additional metadata to attach to the DaskColumn.
    
    Returns:
    DaskColumn: A DaskColumn object representing the input Dask array.
    """

    result = DaskColumn(array.dask, array.name, array.chunks, meta=array)
    if info is not None:
        result.info = info
    return result
y.chunks, meta=array)
    if info is not None:
        result.info = info
    return result
