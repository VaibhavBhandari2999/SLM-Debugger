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
        """
        Fit a polynomial function to the data and return the predicted values.
        
        This function fits a polynomial of a specified order to the input data and returns the predicted values for a range of x-values.
        
        Parameters:
        data (dict): A dictionary containing the input data with keys "x" and "y".
        
        Keyword Arguments:
        order (int): The degree of the polynomial to fit. Default is 1.
        gridsize (int): The number of points to use for the predicted values. Default is
        """


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

        return (
            groupby
            .apply(data.dropna(subset=["x", "y"]), self._fit_predict)
        )


@dataclass
class OLSFit(Stat):

    ...
