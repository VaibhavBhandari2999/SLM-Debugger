######################## BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301  USA
######################### END LICENSE BLOCK #########################

__version__ = "2.0.1"

def detect(aBuf):
    """
    Detect the encoding of a given buffer of bytes.
    
    This function uses a UniversalDetector to analyze a buffer of bytes and determine the encoding used. It returns a dictionary containing the detected encoding and other relevant information.
    
    Parameters:
    aBuf (bytes): The buffer of bytes to analyze.
    
    Returns:
    dict: A dictionary with the following keys:
    - 'encoding': The detected character encoding (e.g., 'utf-8', 'ascii').
    - 'confidence': The confidence level of the detection
    """

    from . import universaldetector
    u = universaldetector.UniversalDetector()
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result
