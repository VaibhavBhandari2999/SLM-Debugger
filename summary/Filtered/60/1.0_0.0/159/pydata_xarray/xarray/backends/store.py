from .. import conventions
from ..core.dataset import Dataset
from .common import BACKEND_ENTRYPOINTS, AbstractDataStore, BackendEntrypoint


class StoreBackendEntrypoint(BackendEntrypoint):
    def guess_can_open(self, store_spec):
        return isinstance(store_spec, AbstractDataStore)

    def open_dataset(
        """
        Open a dataset from a CF (Climate and Forecast) compliant store.
        
        Parameters:
        store (object): The store from which to load the dataset.
        mask_and_scale (bool, optional): Whether to apply mask and scaling to variables. Default is True.
        decode_times (bool, optional): Whether to decode time coordinates. Default is True.
        concat_characters (bool, optional): Whether to concatenate character arrays. Default is True.
        decode_coords (bool, optional): Whether to decode coordinate
        """

        self,
        store,
        *,
        mask_and_scale=True,
        decode_times=True,
        concat_characters=True,
        decode_coords=True,
        drop_variables=None,
        use_cftime=None,
        decode_timedelta=None,
    ):
        vars, attrs = store.load()
        encoding = store.get_encoding()

        vars, attrs, coord_names = conventions.decode_cf_variables(
            vars,
            attrs,
            mask_and_scale=mask_and_scale,
            decode_times=decode_times,
            concat_characters=concat_characters,
            decode_coords=decode_coords,
            drop_variables=drop_variables,
            use_cftime=use_cftime,
            decode_timedelta=decode_timedelta,
        )

        ds = Dataset(vars, attrs=attrs)
        ds = ds.set_coords(coord_names.intersection(vars))
        ds.set_close(store.close)
        ds.encoding = encoding

        return ds


BACKEND_ENTRYPOINTS["store"] = StoreBackendEntrypoint
