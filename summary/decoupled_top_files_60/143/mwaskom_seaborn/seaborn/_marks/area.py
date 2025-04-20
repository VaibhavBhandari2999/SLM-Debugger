from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import matplotlib as mpl

from seaborn._marks.base import (
    Mark,
    Mappable,
    MappableBool,
    MappableFloat,
    MappableColor,
    MappableStyle,
    resolve_properties,
    resolve_color,
)


class AreaBase:

    def _plot(self, split_gen, scales, orient):
        """
        Plot polygons using the provided data and parameters.
        
        This function takes a generator that splits the data into subgroups, scales for
        coordinate transformations, and an orientation for plotting. It processes each
        group of data, standardizes coordinates, resolves properties, and collects
        vertices and colors for each polygon. It then adds the polygons to the axes
        using a PolyCollection.
        
        Parameters:
        split_gen (generator): A generator that yields keys, data, and axes for
        each subgroup of data.
        """


        kws = {}

        for keys, data, ax in split_gen():

            kws.setdefault(ax, defaultdict(list))

            data = self._standardize_coordinate_parameters(data, orient)
            resolved = resolve_properties(self, keys, scales)
            verts = self._get_verts(data, orient)

            ax.update_datalim(verts)
            kws[ax]["verts"].append(verts)

            # TODO fill= is not working here properly
            # We could hack a fix, but would be better to handle fill in resolve_color

            kws[ax]["facecolors"].append(resolve_color(self, keys, "", scales))
            kws[ax]["edgecolors"].append(resolve_color(self, keys, "edge", scales))

            kws[ax]["linewidth"].append(resolved["edgewidth"])
            kws[ax]["linestyle"].append(resolved["edgestyle"])

        for ax, ax_kws in kws.items():
            ax.add_collection(mpl.collections.PolyCollection(**ax_kws))

    def _standardize_coordinate_parameters(self, data, orient):
        return data

    def _get_verts(self, data, orient):
        """
        Generate the vertices for a box plot segment.
        
        This function calculates the vertices for a box plot segment based on the provided data and orientation.
        
        Parameters:
        data (pandas.DataFrame): A DataFrame containing the data points for the box plot segment.
        orient (str): The orientation of the box plot segment, either 'x' or 'y'.
        
        Returns:
        numpy.ndarray: A 2D array of vertices, where each row represents a vertex in (x, y) format.
        
        Example:
        """


        dv = {"x": "y", "y": "x"}[orient]
        data = data.sort_values(orient)
        verts = np.concatenate([
            data[[orient, f"{dv}min"]].to_numpy(),
            data[[orient, f"{dv}max"]].to_numpy()[::-1],
        ])
        if orient == "y":
            verts = verts[:, ::-1]
        return verts

    def _legend_artist(self, variables, value, scales):

        keys = {v: value for v in variables}
        resolved = resolve_properties(self, keys, scales)

        return mpl.patches.Patch(
            facecolor=resolve_color(self, keys, "", scales),
            edgecolor=resolve_color(self, keys, "edge", scales),
            linewidth=resolved["edgewidth"],
            linestyle=resolved["edgestyle"],
            **self.artist_kws,
        )


@dataclass
class Area(AreaBase, Mark):
    """
    An interval mark that fills between baseline and data values.
    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(.2, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color")
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(rc="patch.linewidth", )
    edgestyle: MappableStyle = Mappable("-", )

    # TODO should this be settable / mappable?
    baseline: MappableFloat = Mappable(0, grouping=False)

    def _standardize_coordinate_parameters(self, data, orient):
        dv = {"x": "y", "y": "x"}[orient]
        return data.rename(columns={"baseline": f"{dv}min", dv: f"{dv}max"})


@dataclass
class Ribbon(AreaBase, Mark):
    """
    An interval mark that fills between minimum and maximum values.
    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(.2, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color", )
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(0, )
    edgestyle: MappableFloat = Mappable("-", )

    def _standardize_coordinate_parameters(self, data, orient):
        """
        Standardizes coordinate parameters for a given dataset.
        
        This function standardizes the coordinate parameters of a dataset based on the specified orientation.
        
        Parameters:
        data (pandas.DataFrame): The input dataset containing coordinate information.
        orient (str): The orientation of the coordinates. Must be either 'x' or 'y'.
        
        Returns:
        pandas.DataFrame: The standardized dataset with coordinate parameters adjusted according to the specified orientation.
        
        Notes:
        - The function currently does not perform any validation on the input data.
        -
        """

        # dv = {"x": "y", "y": "x"}[orient]
        # TODO assert that all(ymax >= ymin)?
        return data
