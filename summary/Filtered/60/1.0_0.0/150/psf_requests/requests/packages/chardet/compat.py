######################## BEGIN LICENSE BLOCK ########################
# Contributor(s):
#   Ian Cordasco - port to Python
#
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

import sys


if sys.version_info < (3, 0):
    base_str = (str, unicode)
else:
    base_str = (bytes, str)


def wrap_ord(a):
    """
    Wrap the input 'a' with the built-in ord() function if it is a string in Python 2, otherwise return 'a' as is. This function is designed to handle both Python 2 and Python 3 compatibility for obtaining the Unicode code point of a single character.
    
    Parameters:
    a (str or int): The input character or its Unicode code point.
    
    Returns:
    int: The Unicode code point of the input character, or the input itself if it is an integer.
    
    Note
    """

    if sys.version_info < (3, 0) and isinstance(a, base_str):
        return ord(a)
    else:
        return a
