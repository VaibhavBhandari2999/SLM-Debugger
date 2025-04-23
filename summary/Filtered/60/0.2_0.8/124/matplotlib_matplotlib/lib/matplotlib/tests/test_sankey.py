from matplotlib.sankey import Sankey


def test_sankey():
    # lets just create a sankey instance and check the code runs
    sankey = Sankey()
    sankey.add()


def test_label():
    s = Sankey(flows=[0.25], labels=['First'], orientations=[-1])
    assert s.diagrams[0].texts[0].get_text() == 'First\n0.25'


def test_format_using_callable():
    """
    Format the flow values using a callable function.
    
    This function creates a Sankey diagram with a single flow and label, and formats
    the flow value using a provided callable function. The callable function should
    take a single value as input and return a formatted string.
    
    Parameters:
    show_three_decimal_places (callable): A function that takes a single value
    and returns a formatted string.
    
    Returns:
    Sankey: A Sankey diagram object with a single flow and label, where the
    flow
    """

    # test using callable by slightly incrementing above label example

    def show_three_decimal_places(value):
        return f'{value:.3f}'

    s = Sankey(flows=[0.25], labels=['First'], orientations=[-1],
               format=show_three_decimal_places)

    assert s.diagrams[0].texts[0].get_text() == 'First\n0.250'
