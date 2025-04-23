
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, cast
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

import numpy as np
from pandas import DataFrame

from seaborn._core.scales import Scale
from seaborn._core.groupby import GroupBy
from seaborn._stats.base import Stat
from seaborn.utils import _version_predates


# From https://github.com/numpy/numpy/blob/main/numpy/lib/function_base.pyi
_MethodKind = Literal[
    "inverted_cdf",
    "averaged_inverted_cdf",
    "closest_observation",
    "interpolated_inverted_cdf",
    "hazen",
    "weibull",
    "linear",
    "median_unbiased",
    "normal_unbiased",
    "lower",
    "higher",
    "midpoint",
    "nearest",
]


@dataclass
class Perc(Stat):
    """
    Replace observations with percentile values.

    Parameters
    ----------
    k : list of numbers or int
        If a list of numbers, this gives the percentiles (in [0, 100]) to compute.
        If an integer, compute `k` evenly-spaced percentiles between 0 and 100.
        For example, `k=5` computes the 0, 25, 50, 75, and 100th percentiles.
    method : str
        Method for interpolating percentiles between observed datapoints.
        See :func:`numpy.percentile` for valid options and more information.

    Examples
    --------
    .. include:: ../docstrings/objects.Perc.rst

    """
    k: int | list[float] = 5
    method: str = "linear"

    group_by_orient: ClassVar[bool] = True

    def _percentile(self, data: DataFrame, var: str) -> DataFrame:

        k = list(np.linspace(0, 100, self.k)) if isinstance(self.k, int) else self.k
        method = cast(_MethodKind, self.method)
        values = data[var].dropna()
        if _version_predates(np, "1.22"):
            res = np.percentile(values, k, interpolation=method)  # type: ignore
        else:
            res = np.percentile(data[var].dropna(), k, method=method)
        return DataFrame({var: res, "percentile": k})

    def __call__(
        """
        Calculate the percentile of a specified variable within each group of a DataFrame.
        
        This function computes the percentile of a specified variable within each group of a DataFrame.
        
        Parameters:
        data (DataFrame): The input DataFrame containing the data.
        groupby (GroupBy): The GroupBy object used to group the data.
        orient (str): The orientation of the data, either 'x' or 'y', which determines the variable to compute the percentile on.
        scales (dict[str, Scale]): A dictionary
        """

        self, data: DataFrame, groupby: GroupBy, orient: str, scales: dict[str, Scale],
    ) -> DataFrame:

        var = {"x": "y", "y": "x"}[orient]
        return groupby.apply(data, self._percentile, var)
