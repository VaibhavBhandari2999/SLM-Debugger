import numpy as np

import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=['agg_filter_alpha'],
                  extensions=['png', 'pdf'])
def test_agg_filter_alpha():
    """
    Apply a custom alpha filter to a pcolormesh plot.
    
    This function demonstrates how to apply a custom alpha filter to a pcolormesh
    plot using the `set_agg_filter` method. The filter modifies the alpha channel
    of the image data. Note that for the filter to have an effect, rasterization
    must be enabled for the mesh.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function sets the alpha channel of the image data to 0.
    """

    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    ax = plt.axes()
    x, y = np.mgrid[0:7, 0:8]
    data = x**2 - y**2
    mesh = ax.pcolormesh(data, cmap='Reds', zorder=5)

    def manual_alpha(im, dpi):
        im[:, :, 3] *= 0.6
        print('CALLED')
        return im, 0, 0

    # Note: Doing alpha like this is not the same as setting alpha on
    # the mesh itself. Currently meshes are drawn as independent patches,
    # and we see fine borders around the blocks of color. See the SO
    # question for an example: https://stackoverflow.com/q/20678817/
    mesh.set_agg_filter(manual_alpha)

    # Currently we must enable rasterization for this to have an effect in
    # the PDF backend.
    mesh.set_rasterized(True)

    ax.plot([0, 4, 7], [1, 3, 8])
