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
    Test a Jupyter notebook for proper execution.
    
    This function runs a specified Jupyter notebook and checks for any errors during execution. The notebook is first converted to a Python script and then executed. The function captures any errors generated during the execution and asserts that the notebook ran without any errors.
    
    Parameters:
    nb_path (Path): The path to the Jupyter notebook to be tested.
    
    Returns:
    None: The function does not return any value. It asserts that the notebook executed without any errors.
    
    Key
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
