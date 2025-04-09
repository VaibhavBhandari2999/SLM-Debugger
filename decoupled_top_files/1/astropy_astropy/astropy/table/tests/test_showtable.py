import os
import re

import numpy as np
import pytest

from astropy.table.scripts import showtable

ROOT = os.path.abspath(os.path.dirname(__file__))
ASCII_ROOT = os.path.join(ROOT, "..", "..", "io", "ascii", "tests")
FITS_ROOT = os.path.join(ROOT, "..", "..", "io", "fits", "tests")
VOTABLE_ROOT = os.path.join(ROOT, "..", "..", "io", "votable", "tests")


def test_missing_file(capsys):
    """
    Test the behavior of the `showtable` module when a missing file is provided.
    
    Args:
    capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
    
    Summary:
    This function tests the `showtable.main()` function by passing a non-existent file path ("foobar.fits") as an argument. It then checks if the error message generated matches the expected error message indicating that the specified file does not exist.
    
    Returns:
    None
    """

    showtable.main(["foobar.fits"])
    out, err = capsys.readouterr()
    assert err.startswith("ERROR: [Errno 2] No such file or directory: 'foobar.fits'")


def test_info(capsys):
    """
    Test the info functionality of the showtable module.
    
    Args:
    capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
    
    Summary:
    This function tests the info functionality of the showtable module by running the main function with a FITS file path and the '--info' argument. It then captures the output and checks if it matches the expected output using an assertion statement.
    
    Important Functions:
    - `showtable.main`: The main function of the showtable module that
    """

    showtable.main([os.path.join(FITS_ROOT, "data/table.fits"), "--info"])
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "<Table length=3>",
        " name   dtype ",
        "------ -------",
        "target bytes20",
        " V_mag float32",
    ]


def test_stats(capsys):
    """
    Test the stats functionality of the showtable module.
    
    This function tests the stats functionality of the showtable module by running the main function with a FITS file containing table data and the '--stats' argument. The output is captured and compared against an expected output, allowing for platform-dependent variations in certain values.
    
    Args:
    capsys: A pytest fixture that captures stdout and stderr.
    
    Returns:
    None
    """

    showtable.main([os.path.join(FITS_ROOT, "data/table.fits"), "--stats"])
    out, err = capsys.readouterr()
    expected = [
        "<Table length=3>",
        " name    mean    std   min  max ",
        "------ ------- ------- ---- ----",
        "target      --      --   --   --",
        " V_mag 12.866[0-9]? 1.72111 11.1 15.2",
    ]

    out = out.splitlines()
    assert out[:4] == expected[:4]
    # Here we use re.match as in some cases one of the values above is
    # platform-dependent.
    assert re.match(expected[4], out[4]) is not None


def test_fits(capsys):
    """
    Test the `showtable` module's ability to display FITS table data.
    
    Args:
    capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
    
    Summary:
    This function tests the `showtable.main()` function by passing a FITS file path as an argument. It then captures the output and checks if it matches the expected table format and content.
    
    Expected Output:
    The function expects the following output:
    ```
    target V_mag
    ------- -----
    """

    showtable.main([os.path.join(FITS_ROOT, "data/table.fits")])
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        " target V_mag",
        "------- -----",
        "NGC1001  11.1",
        "NGC1002  12.3",
        "NGC1003  15.2",
    ]


def test_fits_hdu(capsys):
    """
    Test the `showtable` function for displaying HDU data from a FITS file.
    
    This function tests the `showtable.main` method by providing a FITS file
    and a specific HDU (High-Level Data Unit) identifier. It expects to see
    warnings related to units and verifies that the output matches the expected
    table format.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses `pytest.warns` to capture
    """

    from astropy.units import UnitsWarning

    with pytest.warns(UnitsWarning):
        showtable.main(
            [
                os.path.join(FITS_ROOT, "data/zerowidth.fits"),
                "--hdu",
                "AIPS OF",
            ]
        )

    out, err = capsys.readouterr()
    assert out.startswith(
        "   TIME    SOURCE ID ANTENNA NO. SUBARRAY FREQ ID ANT FLAG STATUS 1\n"
        "   DAYS                                                            \n"
        "---------- --------- ----------- -------- ------- -------- --------\n"
        "0.14438657         1          10        1       1        4        4\n"
    )


def test_csv(capsys):
    """
    Test the CSV file rendering functionality.
    
    Args:
    capsys (pytest fixture): Captures stdout and stderr.
    
    Returns:
    None
    
    Summary:
    This function tests the CSV file rendering functionality by using the `showtable.main` function to render a CSV file and then captures the output using the `capsys` fixture. The expected output is compared with the actual output to ensure correctness.
    """

    showtable.main([os.path.join(ASCII_ROOT, "data/simple_csv.csv")])
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        " a   b   c ",
        "--- --- ---",
        "  1   2   3",
        "  4   5   6",
    ]


def test_ascii_format(capsys):
    """
    Test the ASCII format for the `showtable` command.
    
    Args:
    capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
    
    Summary:
    This function tests the `showtable` command with the `ascii.commented_header` format option. It reads data from a file located at `ASCII_ROOT/data/commented_header.dat`, processes it using the specified format, and checks if the output matches the expected result.
    
    Functions Used:
    - `os.path.join`:
    """

    showtable.main(
        [
            os.path.join(ASCII_ROOT, "data/commented_header.dat"),
            "--format",
            "ascii.commented_header",
        ]
    )
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        " a   b   c ",
        "--- --- ---",
        "  1   2   3",
        "  4   5   6",
    ]


def test_ascii_delimiter(capsys):
    """
    Test the ASCII delimiter functionality of the showtable module.
    
    Args:
    capsys (pytest fixture): Captures stdout and stderr.
    
    Summary:
    This function tests the `showtable` module's ability to handle ASCII
    formatted tables with a custom delimiter. It reads data from a file,
    processes it using the `main` function with specified delimiter, and
    verifies the output against expected values.
    
    Usage:
    >>> test_ascii_delimiter(capsys)
    # The
    """

    showtable.main(
        [
            os.path.join(ASCII_ROOT, "data/simple2.txt"),
            "--format",
            "ascii",
            "--delimiter",
            "|",
        ]
    )
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "obsid redshift  X    Y      object   rad ",
        "----- -------- ---- ---- ----------- ----",
        " 3102     0.32 4167 4085 Q1250+568-A  9.0",
        " 3102     0.32 4706 3916 Q1250+568-B 14.0",
        "  877     0.22 4378 3892 'Source 82' 12.5",
    ]


def test_votable(capsys):
    """
    Test votable.
    
    This function tests the votable by running the `showtable.main` function on a specific XML file and table ID. The output is captured using `capsys` and compared against expected values.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The `np.errstate` context manager is used to ignore floating point overflow warnings.
    - The `showtable.main` function is called with the following arguments:
    - Path to the XML
    """

    with np.errstate(over="ignore"):
        # https://github.com/astropy/astropy/issues/13341
        showtable.main(
            [
                os.path.join(VOTABLE_ROOT, "data/regression.xml"),
                "--table-id",
                "main_table",
                "--max-width",
                "50",
            ]
        )
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "   string_test    string_test_2 ...   bitarray2  ",
        "----------------- ------------- ... -------------",
        "    String & test    Fixed stri ... True .. False",
        "String &amp; test    0123456789 ...      -- .. --",
        "             XXXX          XXXX ...      -- .. --",
        "                                ...      -- .. --",
        "                                ...      -- .. --",
    ]


def test_max_lines(capsys):
    """
    Test the max_lines parameter of the showtable function.
    
    Args:
    capsys (pytest fixture): A pytest fixture that captures stdout and stderr.
    
    Returns:
    None
    
    Summary:
    This function tests the `--max-lines` parameter of the `showtable.main()` function by passing a specific file path, format, and maximum number of lines. It then checks if the output matches the expected result.
    """

    showtable.main(
        [
            os.path.join(ASCII_ROOT, "data/cds2.dat"),
            "--format",
            "ascii.cds",
            "--max-lines",
            "7",
            "--max-width",
            "30",
        ]
    )
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "      SST       ... Note",
        "                ...     ",
        "--------------- ... ----",
        "041314.1+281910 ...   --",
        "            ... ...  ...",
        "044427.1+251216 ...   --",
        "044642.6+245903 ...   --",
        "Length = 215 rows",
    ]


def test_show_dtype(capsys):
    """
    Show the data type of columns in a FITS table.
    
    Args:
    capsys: A pytest fixture that captures stdout and stderr.
    
    Returns:
    None
    
    Example:
    >>> test_show_dtype()
    target  V_mag
    bytes20 float32
    ------- -------
    NGC1001    11.1
    NGC1002    12.3
    NGC1003    15.
    """

    showtable.main([os.path.join(FITS_ROOT, "data/table.fits"), "--show-dtype"])
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        " target  V_mag ",
        "bytes20 float32",
        "------- -------",
        "NGC1001    11.1",
        "NGC1002    12.3",
        "NGC1003    15.2",
    ]


def test_hide_unit(capsys):
    """
    Hides the unit column from the output of an ASCII.CDS file.
    
    This function tests the functionality of hiding the unit column in the output
    when using the `showtable` command with the `--hide-unit` option. It reads the
    contents of an ASCII.CDS file, formats it according to the specified options,
    and then checks if the unit column is correctly hidden in the output.
    
    Args:
    capsys: A pytest fixture that captures stdout and stderr.
    """

    showtable.main([os.path.join(ASCII_ROOT, "data/cds.dat"), "--format", "ascii.cds"])
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "Index RAh RAm  RAs  DE- DEd  DEm    DEs   Match Class  AK  Fit ",
        "       h  min   s       deg arcmin arcsec             mag GMsun",
        "----- --- --- ----- --- --- ------ ------ ----- ----- --- -----",
        "    1   3  28 39.09   +  31      6    1.9    --    I*  --  1.35",
    ]

    showtable.main(
        [
            os.path.join(ASCII_ROOT, "data/cds.dat"),
            "--format",
            "ascii.cds",
            "--hide-unit",
        ]
    )
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "Index RAh RAm  RAs  DE- DEd DEm DEs Match Class  AK Fit ",
        "----- --- --- ----- --- --- --- --- ----- ----- --- ----",
        "    1   3  28 39.09   +  31   6 1.9    --    I*  -- 1.35",
    ]
