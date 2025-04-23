from io import BytesIO
import pytest
import logging

from matplotlib import _afm
from matplotlib import font_manager as fm


# See note in afm.py re: use of comma as decimal separator in the
# UnderlineThickness field and re: use of non-ASCII characters in the Notice
# field.
AFM_TEST_DATA = b"""StartFontMetrics 2.0
Comment Comments are ignored.
Comment Creation Date:Mon Nov 13 12:34:11 GMT 2017
FontName MyFont-Bold
EncodingScheme FontSpecific
FullName My Font Bold
FamilyName Test Fonts
Weight Bold
ItalicAngle 0.0
IsFixedPitch false
UnderlinePosition -100
UnderlineThickness 56,789
Version 001.000
Notice Copyright \xa9 2017 No one.
FontBBox 0 -321 1234 369
StartCharMetrics 3
C 0 ; WX 250 ; N space ; B 0 0 0 0 ;
C 42 ; WX 1141 ; N foo ; B 40 60 800 360 ;
C 99 ; WX 583 ; N bar ; B 40 -10 543 210 ;
EndCharMetrics
EndFontMetrics
"""


def test_nonascii_str():
    # This tests that we also decode bytes as utf-8 properly.
    # Else, font files with non ascii characters fail to load.
    inp_str = "привет"
    byte_str = inp_str.encode("utf8")

    ret = _afm._to_str(byte_str)
    assert ret == inp_str


def test_parse_header():
    fh = BytesIO(AFM_TEST_DATA)
    header = _afm._parse_header(fh)
    assert header == {
        b'StartFontMetrics': 2.0,
        b'FontName': 'MyFont-Bold',
        b'EncodingScheme': 'FontSpecific',
        b'FullName': 'My Font Bold',
        b'FamilyName': 'Test Fonts',
        b'Weight': 'Bold',
        b'ItalicAngle': 0.0,
        b'IsFixedPitch': False,
        b'UnderlinePosition': -100,
        b'UnderlineThickness': 56.789,
        b'Version': '001.000',
        b'Notice': b'Copyright \xa9 2017 No one.',
        b'FontBBox': [0, -321, 1234, 369],
        b'StartCharMetrics': 3,
    }


def test_parse_char_metrics():
    fh = BytesIO(AFM_TEST_DATA)
    _afm._parse_header(fh)  # position
    metrics = _afm._parse_char_metrics(fh)
    assert metrics == (
        {0: (250.0, 'space', [0, 0, 0, 0]),
         42: (1141.0, 'foo', [40, 60, 800, 360]),
         99: (583.0, 'bar', [40, -10, 543, 210]),
         },
        {'space': (250.0, 'space', [0, 0, 0, 0]),
         'foo': (1141.0, 'foo', [40, 60, 800, 360]),
         'bar': (583.0, 'bar', [40, -10, 543, 210]),
         })


def test_get_familyname_guessed():
    """
    Retrieve the family name of the font.
    
    This function attempts to retrieve the family name of the font from the AFM file. If the family name is not explicitly provided in the AFM file, it will be guessed based on other available information.
    
    Parameters:
    fh (BytesIO): A BytesIO object containing the AFM file data.
    
    Returns:
    str: The family name of the font.
    
    Example:
    >>> from io import BytesIO
    >>> from afm import AFM
    """

    fh = BytesIO(AFM_TEST_DATA)
    font = _afm.AFM(fh)
    del font._header[b'FamilyName']  # remove FamilyName, so we have to guess
    assert font.get_familyname() == 'My Font'


def test_font_manager_weight_normalization():
    """
    Test the normalization of font weight in the FontManager.
    
    This function checks if the FontManager correctly normalizes the font weight
    to 'normal' when the weight specified in the AFM file is not 'Bold'.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses an AFM (Adobe Font Metric) file to test the weight
    normalization.
    - It replaces the weight entry in the AFM file to 'Custom' and expects the
    FontManager to
    """

    font = _afm.AFM(BytesIO(
        AFM_TEST_DATA.replace(b"Weight Bold\n", b"Weight Custom\n")))
    assert fm.afmFontProperty("", font).weight == "normal"


@pytest.mark.parametrize(
    "afm_data",
    [
        b"""nope
really nope""",
        b"""StartFontMetrics 2.0
Comment Comments are ignored.
Comment Creation Date:Mon Nov 13 12:34:11 GMT 2017
FontName MyFont-Bold
EncodingScheme FontSpecific""",
    ],
)
def test_bad_afm(afm_data):
    fh = BytesIO(afm_data)
    with pytest.raises(RuntimeError):
        _afm._parse_header(fh)


@pytest.mark.parametrize(
    "afm_data",
    [
        b"""StartFontMetrics 2.0
Comment Comments are ignored.
Comment Creation Date:Mon Nov 13 12:34:11 GMT 2017
Aardvark bob
FontName MyFont-Bold
EncodingScheme FontSpecific
StartCharMetrics 3""",
        b"""StartFontMetrics 2.0
Comment Comments are ignored.
Comment Creation Date:Mon Nov 13 12:34:11 GMT 2017
ItalicAngle zero degrees
FontName MyFont-Bold
EncodingScheme FontSpecific
StartCharMetrics 3""",
    ],
)
def test_malformed_header(afm_data, caplog):
    fh = BytesIO(afm_data)
    with caplog.at_level(logging.ERROR):
        _afm._parse_header(fh)

    assert len(caplog.records) == 1
 _afm._parse_header(fh)

    assert len(caplog.records) == 1
