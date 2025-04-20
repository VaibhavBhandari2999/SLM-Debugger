import numpy as np

import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=['agg_filter_alpha'],
                  extensions=['png', 'pdf'])
def test_agg_filter_alpha():
    """
    Test function to demonstrate the use of an alpha filter with pcolormesh.
    
    This function creates a pcolormesh plot and applies a custom alpha filter to
    the mesh. The filter reduces the opacity of the mesh and prints a message
    indicating that the filter has been called. The function also enables
    rasterization for the mesh to ensure the alpha filter has the desired effect.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses `pcol
    """

    # Remove this line when this test image is regenerated.
    plt.rcParams['pcolormesh.snap'] = False

    ax = plt.axes()
    x, y = np.mgrid[0:7, 0:8]
    data = x**2 - y**2
    mesh = ax.pcolormesh(data, cmap='Reds', zorder=5)

    def manual_alpha(im, dpi):
        """
        Apply a manual alpha channel adjustment to an image.
        
        This function modifies the alpha channel of an image to reduce its opacity.
        
        Parameters:
        im (numpy.ndarray): The input image as a NumPy array.
        dpi (int): The dots per inch (DPI) value for the image.
        
        Returns:
        tuple: A tuple containing the modified image, and two zero-valued integers (x_offset, y_offset).
        
        Notes:
        - The alpha channel of the image is multiplied by 0.
        """

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
