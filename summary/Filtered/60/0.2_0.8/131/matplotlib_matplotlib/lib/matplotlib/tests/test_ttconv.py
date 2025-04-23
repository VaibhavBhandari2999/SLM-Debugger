from pathlib import Path

import matplotlib
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt


@image_comparison(["truetype-conversion.pdf"])
# mpltest.ttf does not have "l"/"p" glyphs so we get a warning when trying to
# get the font extents.
def test_truetype_conversion(recwarn):
    """
    Converts a TrueType font to PDF format for use in a matplotlib plot.
    
    This function sets the 'pdf.fonttype' parameter to 3, indicating that the font should be converted to PDF format. It then creates a matplotlib figure and axis, and adds text to the axis using a specified TrueType font file. The text is set to a large font size and positioned at the origin. The x and y ticks are removed from the axis.
    
    Parameters:
    None
    
    Returns:
    fig, ax:
    """

    matplotlib.rcParams['pdf.fonttype'] = 3
    fig, ax = plt.subplots()
    ax.text(0, 0, "ABCDE",
            font=Path(__file__).with_name("mpltest.ttf"), fontsize=80)
    ax.set_xticks([])
    ax.set_yticks([])
