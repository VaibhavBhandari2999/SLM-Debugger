# Licensed under a 3-clause BSD style license - see LICENSE.rst

import io

import pytest

from ..xml import check, unescaper, writer


def test_writer():
    fh = io.StringIO()
    w = writer.XMLWriter(fh)
    with w.tag("html"):
        with w.tag("body"):
            w.data("This is the content")
            w.comment("comment")

    value = ''.join(fh.getvalue().split())
    assert value == '<html><body>Thisisthecontent<!--comment--></body></html>'


def test_check_id():
    """
    Function to validate a given ID string according to specific rules.
    
    Parameters:
    id_str (str): The ID string to be validated.
    
    Returns:
    bool: True if the ID string is valid, False otherwise.
    
    Key Rules:
    - The ID must start with a letter (either uppercase or lowercase).
    - The ID can contain letters (both uppercase and lowercase), digits, and underscores.
    - The ID cannot start with a digit.
    - The ID can be of any length.
    
    Examples:
    >>> test
    """

    assert check.check_id("Fof32")
    assert check.check_id("_Fof32")
    assert not check.check_id("32Fof")


def test_fix_id():
    assert check.fix_id("Fof32") == "Fof32"
    assert check.fix_id("@#f") == "___f"


def test_check_token():
    assert check.check_token("token")
    assert not check.check_token("token\rtoken")


def test_check_mime_content_type():
    assert check.check_mime_content_type("image/jpeg")
    assert not check.check_mime_content_type("image")


def test_check_anyuri():
    assert check.check_anyuri("https://github.com/astropy/astropy")


def test_unescape_all():
    # str
    url_in = 'http://casu.ast.cam.ac.uk/ag/iphas-dsa%2FSubmitCone?' \
             'DSACAT=IDR&amp;amp;DSATAB=Emitters&amp;amp;'
    url_out = 'http://casu.ast.cam.ac.uk/ag/iphas-dsa/SubmitCone?' \
              'DSACAT=IDR&DSATAB=Emitters&'
    assert unescaper.unescape_all(url_in) == url_out

    # bytes
    url_in = b'http://casu.ast.cam.ac.uk/ag/iphas-dsa%2FSubmitCone?' \
             b'DSACAT=IDR&amp;amp;DSATAB=Emitters&amp;amp;'
    url_out = b'http://casu.ast.cam.ac.uk/ag/iphas-dsa/SubmitCone?' \
              b'DSACAT=IDR&DSATAB=Emitters&'
    assert unescaper.unescape_all(url_in) == url_out


def test_escape_xml():
    """
    Escape special characters for XML.
    
    This function escapes special characters in a given string or bytes object for safe inclusion in XML content. It returns a string or bytes object with the following characters replaced:
    - '&' is replaced with '&amp;'
    - All other special characters are left unchanged.
    
    Parameters:
    s (str or bytes): The input string or bytes object to be escaped.
    
    Returns:
    str or bytes: The escaped string or bytes object.
    
    Examples:
    >>> test_escape_xml()
    True
    """

    s = writer.xml_escape('This & That')
    assert type(s) == str
    assert s == 'This &amp; That'

    s = writer.xml_escape(1)
    assert type(s) == str
    assert s == '1'

    s = writer.xml_escape(b'This & That')
    assert type(s) == bytes
    assert s == b'This &amp; That'


@pytest.mark.skipif('writer.HAS_BLEACH')
def test_escape_xml_without_bleach():
    fh = io.StringIO()
    w = writer.XMLWriter(fh)

    with pytest.raises(ValueError) as err:
        with w.xml_cleaning_method('bleach_clean'):
            pass
    assert 'bleach package is required when HTML escaping is disabled' in str(err)


@pytest.mark.skipif('not writer.HAS_BLEACH')
def test_escape_xml_with_bleach():
    fh = io.StringIO()
    w = writer.XMLWriter(fh)

    # Turn off XML escaping, but still sanitize unsafe tags like <script>
    with w.xml_cleaning_method('bleach_clean'):
        w.start('td')
        w.data('<script>x</script> <em>OK</em>')
        w.end(indent=False)
    assert fh.getvalue() == '<td>&lt;script&gt;x&lt;/script&gt; <em>OK</em></td>\n'

    fh = io.StringIO()
    w = writer.XMLWriter(fh)

    # Default is True (all XML tags escaped)
    with w.xml_cleaning_method():
        w.start('td')
        w.data('<script>x</script> <em>OK</em>')
        w.end(indent=False)
    assert fh.getvalue() == '<td>&lt;script&gt;x&lt;/script&gt; &lt;em&gt;OK&lt;/em&gt;</td>\n'
