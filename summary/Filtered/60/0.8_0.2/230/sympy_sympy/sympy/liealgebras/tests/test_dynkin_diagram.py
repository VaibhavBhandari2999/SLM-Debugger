from sympy.liealgebras.dynkin_diagram import DynkinDiagram

def test_DynkinDiagram():
    """
    Function to test the DynkinDiagram class.
    
    This function checks the functionality of the DynkinDiagram class by creating instances with different types of Dynkin diagrams and comparing the output to expected string representations.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Creates a DynkinDiagram instance for type "A3" and compares its string representation to the expected Dynkin diagram.
    - Creates a DynkinDiagram instance for type "B3" and compares its string representation to the expected
    """

    c = DynkinDiagram("A3")
    diag = "0---0---0\n1   2   3"
    assert c == diag
    ct = DynkinDiagram(["B", 3])
    diag2 = "0---0=>=0\n1   2   3"
    assert ct == diag2
