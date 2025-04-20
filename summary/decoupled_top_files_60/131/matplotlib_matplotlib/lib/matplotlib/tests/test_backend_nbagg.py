import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import pytest

nbformat = pytest.importorskip('nbformat')
pytest.importorskip('nbconvert')
pytest.importorskip('ipykernel')

# From https://blog.thedataincubator.com/2016/06/testing-jupyter-notebooks/


def test_ipynb():
    """
    Executes a Jupyter notebook and verifies that it runs without errors.
    
    This function takes a Jupyter notebook file and converts it to a Python notebook, executing it with a timeout of 500 seconds. The executed notebook is saved to a temporary directory. The function then checks for any error outputs in the executed notebook and asserts that no errors were encountered.
    
    Parameters:
    - nb_path (Path): The path to the input Jupyter notebook file.
    
    Returns:
    - None: The function does not return
    """

    nb_path = Path(__file__).parent / 'test_nbagg_01.ipynb'

    with TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir, "out.ipynb")
        subprocess.check_call(
            ["jupyter", "nbconvert", "--to", "notebook",
             "--execute", "--ExecutePreprocessor.timeout=500",
             "--output", str(out_path), str(nb_path)],
            env={**os.environ, "IPYTHONDIR": tmpdir})
        with out_path.open() as out:
            nb = nbformat.read(out, nbformat.current_nbformat)

    errors = [output for cell in nb.cells for output in cell.get("outputs", [])
              if output.output_type == "error"]
    assert not errors
