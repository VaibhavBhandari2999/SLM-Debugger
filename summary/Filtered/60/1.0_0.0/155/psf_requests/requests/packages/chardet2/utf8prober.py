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

from . import constants
import sys
from .constants import eStart, eError, eItsMe
from .charsetprober import CharSetProber
from .codingstatemachine import CodingStateMachine
from .mbcssm import UTF8SMModel

ONE_CHAR_PROB = 0.5

class UTF8Prober(CharSetProber):
    def __init__(self):
        """
        Initialize the character set prober.
        
        This method initializes the character set prober using the provided UTF8SMModel for the coding state machine. It sets up the initial state and resets the prober.
        
        Parameters:
        None
        
        Attributes:
        _mCodingSM (CodingStateMachine): The coding state machine initialized with UTF8SMModel.
        
        Methods Called:
        reset: Resets the prober to its initial state.
        
        Note:
        This method is typically called during the object's initialization.
        """

        CharSetProber.__init__(self)
        self._mCodingSM = CodingStateMachine(UTF8SMModel)
        self.reset()

    def reset(self):
        CharSetProber.reset(self)
        self._mCodingSM.reset()
        self._mNumOfMBChar = 0

    def get_charset_name(self):
        return "utf-8"

    def feed(self, aBuf):
        for c in aBuf:
            codingState = self._mCodingSM.next_state(c)
            if codingState == eError:
                self._mState = constants.eNotMe
                break
            elif codingState == eItsMe:
                self._mState = constants.eFoundIt
                break
            elif codingState == eStart:
                if self._mCodingSM.get_current_charlen() >= 2:
                    self._mNumOfMBChar += 1

        if self.get_state() == constants.eDetecting:
            if self.get_confidence() > constants.SHORTCUT_THRESHOLD:
                self._mState = constants.eFoundIt

        return self.get_state()

    def get_confidence(self):
        """
        Function to calculate the confidence level based on the number of characters and a predefined probability.
        
        Parameters:
        self (object): The object instance that contains the following attributes:
        - _mNumOfMBChar (int): The number of multi-byte characters.
        - _mNumOfChar (int): The number of characters (not used in the function).
        - ONE_CHAR_PROB (float): The probability of a single character (default is 0.01).
        
        Returns:
        """

        unlike = 0.99
        if self._mNumOfMBChar < 6:
            for i in range(0, self._mNumOfMBChar):
                unlike = unlike * ONE_CHAR_PROB
            return 1.0 - unlike
        else:
            return unlike
