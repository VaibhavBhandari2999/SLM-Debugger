from sympy.liealgebras.dynkin_diagram import DynkinDiagram

def test_DynkinDiagram():
    """
    Function to test the creation of Dynkin diagrams.
    
    This function checks the creation of Dynkin diagrams for given types and ranks.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The Dynkin diagram for "A3" should match the expected string "0---0---0\n1   2   3".
    - The Dynkin diagram for "B3" should match the expected string "0---0=>=0\n1   2   3".
    """

    c = DynkinDiagram("A3")
    diag = "0---0---0\n1   2   3"
    assert c == diag
    ct = DynkinDiagram(["B", 3])
    diag2 = "0---0=>=0\n1   2   3"
    assert ct == diag2
