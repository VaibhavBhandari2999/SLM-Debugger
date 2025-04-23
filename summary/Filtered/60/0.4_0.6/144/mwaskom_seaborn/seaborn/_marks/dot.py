from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import matplotlib as mpl

from seaborn._marks.base import (
    Mark,
    Mappable,
    MappableBool,
    MappableFloat,
    MappableString,
    MappableColor,
    MappableStyle,
    resolve_properties,
    resolve_color,
    document_properties,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from matplotlib.artist import Artist
    from seaborn._core.scales import Scale


class DotBase(Mark):

    def _resolve_paths(self, data):
        """
        Resolves and returns the transformed paths for markers in a given data structure.
        
        This function processes a dictionary containing marker information and returns a list of transformed paths for the markers. If a single `MarkerStyle` object is provided, it returns the transformed path directly. If multiple markers are provided, it caches the transformed paths to avoid redundant computations.
        
        Parameters:
        data (dict): A dictionary containing marker information. The dictionary must have a key "marker" that points to a list of `Path` objects
        """


        paths = []
        path_cache = {}
        marker = data["marker"]

        def get_transformed_path(m):
            return m.get_path().transformed(m.get_transform())

        if isinstance(marker, mpl.markers.MarkerStyle):
            return get_transformed_path(marker)

        for m in marker:
            if m not in path_cache:
                path_cache[m] = get_transformed_path(m)
            paths.append(path_cache[m])
        return paths

    def _resolve_properties(self, data, scales):
        """
        Resolves and processes properties for a given data set and scales.
        
        This function takes a data set and scales as input, resolves the properties, and processes them according to specific rules. The function returns a dictionary containing the resolved properties.
        
        Parameters:
        data (dict or list): The data set for which properties need to be resolved.
        scales (dict): The scales used for property resolution.
        
        Returns:
        dict: A dictionary containing the resolved properties, including 'path', 'size', and 'fill
        """


        resolved = resolve_properties(self, data, scales)
        resolved["path"] = self._resolve_paths(resolved)
        resolved["size"] = resolved["pointsize"] ** 2

        if isinstance(data, dict):  # Properties for single dot
            filled_marker = resolved["marker"].is_filled()
        else:
            filled_marker = [m.is_filled() for m in resolved["marker"]]

        resolved["fill"] = resolved["fill"] * filled_marker

        return resolved

    def _plot(self, split_gen, scales, orient):

        # TODO Not backcompat with allowed (but nonfunctional) univariate plots
        # (That should be solved upstream by defaulting to "" for unset x/y?)
        # (Be mindful of xmin/xmax, etc!)

        for _, data, ax in split_gen():

            offsets = np.column_stack([data["x"], data["y"]])
            data = self._resolve_properties(data, scales)

            points = mpl.collections.PathCollection(
                offsets=offsets,
                paths=data["path"],
                sizes=data["size"],
                facecolors=data["facecolor"],
                edgecolors=data["edgecolor"],
                linewidths=data["linewidth"],
                linestyles=data["edgestyle"],
                transOffset=ax.transData,
                transform=mpl.transforms.IdentityTransform(),
                **self.artist_kws,
            )
            ax.add_collection(points)

    def _legend_artist(
        self, variables: list[str], value: Any, scales: dict[str, Scale],
    ) -> Artist:

        key = {v: value for v in variables}
        res = self._resolve_properties(key, scales)

        return mpl.collections.PathCollection(
            paths=[res["path"]],
            sizes=[res["size"]],
            facecolors=[res["facecolor"]],
            edgecolors=[res["edgecolor"]],
            linewidths=[res["linewidth"]],
            linestyles=[res["edgestyle"]],
            transform=mpl.transforms.IdentityTransform(),
            **self.artist_kws,
        )


@document_properties
@dataclass
class Dot(DotBase):
    """
    A mark suitable for dot plots or less-dense scatterplots.

    See also
    --------
    Dots : A dot mark defined by strokes to better handle overplotting.

    Examples
    --------
    .. include:: ../docstrings/objects.Dot.rst

    """
    marker: MappableString = Mappable("o", grouping=False)
    pointsize: MappableFloat = Mappable(6, grouping=False)  # TODO rcParam?
    stroke: MappableFloat = Mappable(.75, grouping=False)  # TODO rcParam?
    color: MappableColor = Mappable("C0", grouping=False)
    alpha: MappableFloat = Mappable(1, grouping=False)
    fill: MappableBool = Mappable(True, grouping=False)
    edgecolor: MappableColor = Mappable(depend="color", grouping=False)
    edgealpha: MappableFloat = Mappable(depend="alpha", grouping=False)
    edgewidth: MappableFloat = Mappable(.5, grouping=False)  # TODO rcParam?
    edgestyle: MappableStyle = Mappable("-", grouping=False)

    def _resolve_properties(self, data, scales):
        """
        Resolves and modifies properties for a plot element.
        
        This function processes the input data and scales to resolve and modify the properties of a plot element. It handles the resolution of fill, stroke, and edge properties, and adjusts the colors and line widths accordingly.
        
        Parameters:
        data (array-like): The input data for the plot element.
        scales (dict): A dictionary containing scale information for the plot.
        
        Returns:
        dict: A dictionary containing the resolved properties, including 'fill', 'stroke',
        """


        resolved = super()._resolve_properties(data, scales)
        filled = resolved["fill"]

        main_stroke = resolved["stroke"]
        edge_stroke = resolved["edgewidth"]
        resolved["linewidth"] = np.where(filled, edge_stroke, main_stroke)

        main_color = resolve_color(self, data, "", scales)
        edge_color = resolve_color(self, data, "edge", scales)

        if not np.isscalar(filled):
            # Expand dims to use in np.where with rgba arrays
            filled = filled[:, None]
        resolved["edgecolor"] = np.where(filled, edge_color, main_color)

        filled = np.squeeze(filled)
        if isinstance(main_color, tuple):
            # TODO handle this in resolve_color
            main_color = tuple([*main_color[:3], main_color[3] * filled])
        else:
            main_color = np.c_[main_color[:, :3], main_color[:, 3] * filled]
        resolved["facecolor"] = main_color

        return resolved


@document_properties
@dataclass
class Dots(DotBase):
    """
    A dot mark defined by strokes to better handle overplotting.

    See also
    --------
    Dot : A mark suitable for dot plots or less-dense scatterplots.

    Examples
    --------
    .. include:: ../docstrings/objects.Dots.rst

    """
    # TODO retype marker as MappableMarker
    marker: MappableString = Mappable(rc="scatter.marker", grouping=False)
    pointsize: MappableFloat = Mappable(4, grouping=False)  # TODO rcParam?
    stroke: MappableFloat = Mappable(.75, grouping=False)  # TODO rcParam?
    color: MappableColor = Mappable("C0", grouping=False)
    alpha: MappableFloat = Mappable(1, grouping=False)  # TODO auto alpha?
    fill: MappableBool = Mappable(True, grouping=False)
    fillcolor: MappableColor = Mappable(depend="color", grouping=False)
    fillalpha: MappableFloat = Mappable(.2, grouping=False)

    def _resolve_properties(self, data, scales):
        """
        Resolves and updates properties for a graphical object.
        
        This method updates the properties of a graphical object by resolving and modifying certain attributes. It takes the original properties and scales, and returns an updated dictionary of properties.
        
        Parameters:
        data (dict): A dictionary containing the data and metadata for the graphical object.
        scales (dict): A dictionary containing the scales used for mapping data to visual properties.
        
        Returns:
        dict: A dictionary containing the updated properties of the graphical object, including modified attributes such as
        """


        resolved = super()._resolve_properties(data, scales)
        resolved["linewidth"] = resolved.pop("stroke")
        resolved["facecolor"] = resolve_color(self, data, "fill", scales)
        resolved["edgecolor"] = resolve_color(self, data, "", scales)
        resolved.setdefault("edgestyle", (0, None))

        fc = resolved["facecolor"]
        if isinstance(fc, tuple):
            resolved["facecolor"] = fc[0], fc[1], fc[2], fc[3] * resolved["fill"]
        else:
            fc[:, 3] = fc[:, 3] * resolved["fill"]  # TODO Is inplace mod a problem?
            resolved["facecolor"] = fc

        return resolved
