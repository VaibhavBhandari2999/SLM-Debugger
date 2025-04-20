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
    Wrap the input 'a' to return its ordinal value if it's a string (for Python 2) or return 'a' as is for Python 3.
    
    Parameters:
    a (str or int): The input value which can be a string or an integer.
    
    Returns:
    int: The ordinal value of the character if 'a' is a string, or 'a' itself if it's an integer.
    
    Notes:
    - For Python 2, this function returns the ordinal value
    """

    if sys.version_info < (3, 0) and isinstance(a, base_str):
        return ord(a)
    else:
        return a
