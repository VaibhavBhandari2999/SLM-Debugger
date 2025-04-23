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
    Wrap the input 'a' with the built-in ord() function. If the Python version is less than 3.0 and 'a' is an instance of base_str, return the result of ord(a). Otherwise, return 'a' as is.
    
    Parameters:
    a (any): The input value to be wrapped.
    
    Returns:
    int or any: The result of ord(a) if the version is less than 3.0 and 'a' is an instance of base_str, otherwise returns
    """

    if sys.version_info < (3, 0) and isinstance(a, base_str):
        return ord(a)
    else:
        return a
