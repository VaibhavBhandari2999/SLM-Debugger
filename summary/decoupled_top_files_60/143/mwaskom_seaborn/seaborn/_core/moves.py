from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Callable, Optional, Union

import numpy as np
from pandas import DataFrame

from seaborn._core.groupby import GroupBy


@dataclass
class Move:

    group_by_orient: ClassVar[bool] = True

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:
        raise NotImplementedError


@dataclass
class Jitter(Move):
    """
    Random displacement of marks along either or both axes to reduce overplotting.
    """
    width: float = 0
    x: float = 0
    y: float = 0

    seed: Optional[int] = None

    # TODO what is the best way to have a reasonable default?
    # The problem is that "reasonable" seems dependent on the mark

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:

        # TODO is it a problem that GroupBy is not used for anything here?
        # Should we type it as optional?

        data = data.copy()

        rng = np.random.default_rng(self.seed)

        def jitter(data, col, scale):
            noise = rng.uniform(-.5, +.5, len(data))
            offsets = noise * scale
            return data[col] + offsets

        if self.width:
            data[orient] = jitter(data, orient, self.width * data["width"])
        if self.x:
            data["x"] = jitter(data, "x", self.x)
        if self.y:
            data["y"] = jitter(data, "y", self.y)

        return data


@dataclass
class Dodge(Move):
    """
    Displacement and narrowing of overlapping marks along orientation axis.
    """
    empty: str = "keep"  # Options: keep, drop, fill
    gap: float = 0

    # TODO accept just a str here?
    # TODO should this always be present?
    # TODO should the default be an "all" singleton?
    by: Optional[list[str]] = None

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:
        """
        Dodge the positions of elements in a DataFrame based on a specified orientation.
        
        This function modifies the positions of elements in a DataFrame by dodging them based on a specified orientation. The dodging is performed by adjusting the widths and offsets of the elements.
        
        Parameters:
        data (DataFrame): The input DataFrame containing the data to be dodged.
        groupby (GroupBy): The GroupBy object used for grouping and aggregation.
        orient (str): The orientation along which the dodging should be performed
        """


        grouping_vars = [v for v in groupby.order if v in data]
        groups = groupby.agg(data, {"width": "max"})
        if self.empty == "fill":
            groups = groups.dropna()

        def groupby_pos(s):
            grouper = [groups[v] for v in [orient, "col", "row"] if v in data]
            return s.groupby(grouper, sort=False, observed=True)

        def scale_widths(w):
            """
            Scales the widths of a given series.
            
            This function scales the widths of a pandas Series by normalizing the sum of the values to 1 and then scaling them to the maximum value in the original series. Missing values can be filled with the mean of the existing values or a specified fill value.
            
            Parameters:
            w (pandas.Series): The series of widths to be scaled.
            
            Keyword Arguments:
            empty (str): Determines how to handle missing values. Can be either "fill" (default
            """

            # TODO what value to fill missing widths??? Hard problem...
            # TODO short circuit this if outer widths has no variance?
            empty = 0 if self.empty == "fill" else w.mean()
            filled = w.fillna(empty)
            scale = filled.max()
            norm = filled.sum()
            if self.empty == "keep":
                w = filled
            return w / norm * scale

        def widths_to_offsets(w):
            return w.shift(1).fillna(0).cumsum() + (w - w.sum()) / 2

        new_widths = groupby_pos(groups["width"]).transform(scale_widths)
        offsets = groupby_pos(new_widths).transform(widths_to_offsets)

        if self.gap:
            new_widths *= 1 - self.gap

        groups["_dodged"] = groups[orient] + offsets
        groups["width"] = new_widths

        out = (
            data
            .drop("width", axis=1)
            .merge(groups, on=grouping_vars, how="left")
            .drop(orient, axis=1)
            .rename(columns={"_dodged": orient})
        )

        return out


@dataclass
class Stack(Move):
    """
    Displacement of overlapping bar or area marks along the value axis.
    """
    # TODO center? (or should this be a different move, eg. Stream())

    def _stack(self, df, orient):

        # TODO should stack do something with ymin/ymax style marks?
        # Should there be an upstream conversion to baseline/height parameterization?

        if df["baseline"].nunique() > 1:
            err = "Stack move cannot be used when baselines are already heterogeneous"
            raise RuntimeError(err)

        other = {"x": "y", "y": "x"}[orient]
        stacked_lengths = (df[other] - df["baseline"]).dropna().cumsum()
        offsets = stacked_lengths.shift(1).fillna(0)

        df[other] = stacked_lengths
        df["baseline"] = df["baseline"] + offsets

        return df

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:

        # TODO where to ensure that other semantic variables are sorted properly?
        # TODO why are we not using the passed in groupby here?
        groupers = ["col", "row", orient]
        return GroupBy(groupers).apply(data, self._stack, orient)


@dataclass
class Shift(Move):
    """
    Displacement of all marks with the same magnitude / direction.
    """
    x: float = 0
    y: float = 0

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:

        data = data.copy(deep=False)
        data["x"] = data["x"] + self.x
        data["y"] = data["y"] + self.y
        return data


@dataclass
class Norm(Move):
    """
    Divisive scaling on the value axis after aggregating within groups.
    """

    func: Union[Callable, str] = "max"
    where: Optional[str] = None
    by: Optional[list[str]] = None
    percent: bool = False

    group_by_orient: ClassVar[bool] = False

    def _norm(self, df, var):
        """
        Normalize a variable in a DataFrame.
        
        This function normalizes a specified variable in a DataFrame by dividing it by a reference value. The reference value can be the entire column or a subset of the column based on a condition. The result can be optionally converted to a percentage.
        
        Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        var (str): The name of the variable to be normalized.
        
        Keyword Arguments:
        where (str, optional): A boolean condition to filter the DataFrame
        """


        if self.where is None:
            denom_data = df[var]
        else:
            denom_data = df.query(self.where)[var]
        df[var] = df[var] / denom_data.agg(self.func)

        if self.percent:
            df[var] = df[var] * 100

        return df

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:

        other = {"x": "y", "y": "x"}[orient]
        return groupby.apply(data, self._norm, other)


# TODO
# @dataclass
# class Ridge(Move):
#     ...
        if self.where is None:
            denom_data = df[var]
        else:
            denom_data = df.query(self.where)[var]
        df[var] = df[var] / denom_data.agg(self.func)

        if self.percent:
            df[var] = df[var] * 100

        return df

    def __call__(self, data: DataFrame, groupby: GroupBy, orient: str) -> DataFrame:

        other = {"x": "y", "y": "x"}[orient]
        return groupby.apply(data, self._norm, other)


# TODO
# @dataclass
# class Ridge(Move):
#     ...
# @dataclass
# class Ridge(Move):
#     ...
