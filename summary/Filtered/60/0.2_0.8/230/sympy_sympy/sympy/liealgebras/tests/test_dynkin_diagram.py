from sympy.liealgebras.dynkin_diagram import DynkinDiagram

def test_DynkinDiagram():
    """
    Function to test the creation and string representation of Dynkin diagrams.
    
    This function tests the creation of Dynkin diagrams for specific types and ranks, and checks if the string representation matches the expected output.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Creates Dynkin diagrams for types "A3" and "B3".
    - Compares the string representation of the diagrams with expected values.
    """

    c = DynkinDiagram("A3")
    diag = "0---0---0\n1   2   3"
    assert c == diag
    ct = DynkinDiagram(["B", 3])
    diag2 = "0---0=>=0\n1   2   3"
    assert ct == diag2
