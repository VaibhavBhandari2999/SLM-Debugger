from pathlib import Path

import matplotlib
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt


@image_comparison(["truetype-conversion.pdf"])
# mpltest.ttf does not have "l"/"p" glyphs so we get a warning when trying to
# get the font extents.
def test_truetype_conversion(recwarn):
    """
    Converts a TrueType font to PDF format for text rendering in a matplotlib figure.
    
    This function sets the `pdf.fonttype` parameter to 3, indicating that the text should be converted to outlines for better quality in PDF output. It then creates a matplotlib figure and adds a text element using a specified TrueType font file. The text is centered at coordinates (0, 0) and has a font size of 80. The x and y ticks are removed from the plot to clean
    """

    matplotlib.rcParams['pdf.fonttype'] = 3
    fig, ax = plt.subplots()
    ax.text(0, 0, "ABCDE",
            font=Path(__file__).with_name("mpltest.ttf"), fontsize=80)
    ax.set_xticks([])
    ax.set_yticks([])
