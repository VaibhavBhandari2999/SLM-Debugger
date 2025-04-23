######################## BEGIN LICENSE BLOCK ########################
# The Original Code is mozilla.org code.
#
# The Initial Developer of the Original Code is
# Netscape Communications Corporation.
# Portions created by the Initial Developer are Copyright (C) 1998
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Mark Pilgrim - port to Python
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

from .mbcharsetprober import MultiByteCharSetProber
from .codingstatemachine import CodingStateMachine
from .chardistribution import GB2312DistributionAnalysis
from .mbcssm import GB2312SMModel

class GB2312Prober(MultiByteCharSetProber):
    def __init__(self):
        """
        Initialize the GB2312Prober.
        
        This method initializes the prober using the MultiByteCharSetProber's initialization method. It sets up the coding state machine with the GB2312SMModel and configures the distribution analyzer for GB2312. After initialization, it resets the prober to its initial state.
        
        Parameters:
        None
        
        Returns:
        None
        """

        MultiByteCharSetProber.__init__(self)
        self._mCodingSM = CodingStateMachine(GB2312SMModel)
        self._mDistributionAnalyzer = GB2312DistributionAnalysis()
        self.reset()

    def get_charset_name(self):
        return "GB2312"
