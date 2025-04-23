from matplotlib.sankey import Sankey


def test_sankey():
    """
    Create and add a basic Sankey diagram to the current Sankey instance.
    
    This function initializes a Sankey object and adds a basic Sankey diagram to it.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    ```python
    sankey = Sankey()
    sankey.add()
    ```
    """

    # lets just create a sankey instance and check the code runs
    sankey = Sankey()
    sankey.add()


def test_label():
    s = Sankey(flows=[0.25], labels=['First'], orientations=[-1])
    assert s.diagrams[0].texts[0].get_text() == 'First\n0.25'


def test_format_using_callable():
    # test using callable by slightly incrementing above label example

    def show_three_decimal_places(value):
        return f'{value:.3f}'

    s = Sankey(flows=[0.25], labels=['First'], orientations=[-1],
               format=show_three_decimal_places)

    assert s.diagrams[0].texts[0].get_text() == 'First\n0.250'
ow_three_decimal_places(value):
        return f'{value:.3f}'

    s = Sankey(flows=[0.25], labels=['First'], orientations=[-1],
               format=show_three_decimal_places)

    assert s.diagrams[0].texts[0].get_text() == 'First\n0.250'
