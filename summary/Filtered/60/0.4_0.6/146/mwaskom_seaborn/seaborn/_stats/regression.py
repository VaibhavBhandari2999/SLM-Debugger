from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import pandas as pd

from seaborn._stats.base import Stat


@dataclass
class PolyFit(Stat):
    """
    Fit a polynomial of the given order and resample data onto predicted curve.
    """
    # This is a provisional class that is useful for building out functionality.
    # It may or may not change substantially in form or dissappear as we think
    # through the organization of the stats subpackage.

    order: int = 2
    gridsize: int = 100

    def _fit_predict(self, data):

        x = data["x"]
        y = data["y"]
        if x.nunique() <= self.order:
            # TODO warn?
            xx = yy = []
        else:
            p = np.polyfit(x, y, self.order)
            xx = np.linspace(x.min(), x.max(), self.gridsize)
            yy = np.polyval(p, xx)

        return pd.DataFrame(dict(x=xx, y=yy))

    # TODO we should have a way of identifying the method that will be applied
    # and then only define __call__ on a base-class of stats with this pattern

    def __call__(self, data, groupby, orient, scales):
        """
        This function processes the input data by applying a fitting and prediction method to each group defined by the 'groupby' parameter. The function accepts the following parameters:
        
        Parameters:
        data (pandas.DataFrame): The input data containing 'x' and 'y' columns.
        groupby (pandas.core.groupby.DataFrameGroupBy): A groupby object that defines the groups to which the fitting and prediction will be applied.
        orient (str): The orientation of the data, indicating how the data
        """


        return (
            groupby
            .apply(data.dropna(subset=["x", "y"]), self._fit_predict)
        )


@dataclass
class OLSFit(Stat):

    ...
