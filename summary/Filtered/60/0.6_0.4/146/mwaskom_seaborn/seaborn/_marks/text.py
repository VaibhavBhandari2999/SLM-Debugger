from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import matplotlib as mpl
from matplotlib.transforms import ScaledTranslation

from seaborn._marks.base import (
    Mark,
    Mappable,
    MappableFloat,
    MappableString,
    MappableColor,
    resolve_properties,
    resolve_color,
    document_properties,
)


@document_properties
@dataclass
class Text(Mark):
    """
    A textual mark to annotate or represent data values.

    Examples
    --------
    .. include:: ../docstrings/objects.Text.rst

    """
    text: MappableString = Mappable("")
    color: MappableColor = Mappable("k")
    alpha: MappableFloat = Mappable(1)
    fontsize: MappableFloat = Mappable(rc="font.size")
    halign: MappableString = Mappable("center")
    valign: MappableString = Mappable("center_baseline")
    offset: MappableFloat = Mappable(4)

    def _plot(self, split_gen, scales, orient):
        """
        Plots text annotations on a matplotlib axis.
        
        Parameters:
        split_gen (callable): A generator function that yields keys, data, and axes for plotting.
        scales (dict): A dictionary containing scaling factors for text properties.
        orient (str): The orientation of the text annotations.
        
        Returns:
        None: This function modifies the matplotlib axes in place and does not return any value.
        
        This function iterates over the generator `split_gen` to plot text annotations on the provided axes. It resolves the
        """


        ax_data = defaultdict(list)

        for keys, data, ax in split_gen():

            vals = resolve_properties(self, keys, scales)
            color = resolve_color(self, keys, "", scales)

            halign = vals["halign"]
            valign = vals["valign"]
            fontsize = vals["fontsize"]
            offset = vals["offset"] / 72

            offset_trans = ScaledTranslation(
                {"right": -offset, "left": +offset}.get(halign, 0),
                {"top": -offset, "bottom": +offset, "baseline": +offset}.get(valign, 0),
                ax.figure.dpi_scale_trans,
            )

            for row in data.to_dict("records"):
                artist = mpl.text.Text(
                    x=row["x"],
                    y=row["y"],
                    text=str(row.get("text", vals["text"])),
                    color=color,
                    fontsize=fontsize,
                    horizontalalignment=halign,
                    verticalalignment=valign,
                    transform=ax.transData + offset_trans,
                    **self.artist_kws,
                )
                ax.add_artist(artist)
                ax_data[ax].append([row["x"], row["y"]])

        for ax, ax_vals in ax_data.items():
            ax.update_datalim(np.array(ax_vals))
