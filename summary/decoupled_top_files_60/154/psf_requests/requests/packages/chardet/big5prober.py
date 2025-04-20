######################## BEGIN LICENSE BLOCK ########################
# The Original Code is Mozilla Communicator client code.
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
from .chardistribution import Big5DistributionAnalysis
from .mbcssm import Big5SMModel


class Big5Prober(MultiByteCharSetProber):
    def __init__(self):
        """
        Initialize the Big5Prober object.
        
        This method initializes the Big5Prober object, setting up the necessary components for detecting the Big5 character set. It inherits from MultiByteCharSetProber and uses a specific coding state machine (Big5SMModel) and distribution analyzer (Big5DistributionAnalysis) for character set detection.
        
        Parameters:
        None
        
        Attributes Set:
        - _mCodingSM: A CodingStateMachine instance initialized with Big5SMModel.
        - _mDistributionAnalyzer:
        """

        MultiByteCharSetProber.__init__(self)
        self._mCodingSM = CodingStateMachine(Big5SMModel)
        self._mDistributionAnalyzer = Big5DistributionAnalysis()
        self.reset()

    def get_charset_name(self):
        return "Big5"
