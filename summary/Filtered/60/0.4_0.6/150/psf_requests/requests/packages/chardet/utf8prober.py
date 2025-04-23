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
from .charsetprober import CharSetProber
from .codingstatemachine import CodingStateMachine
from .mbcssm import UTF8SMModel

ONE_CHAR_PROB = 0.5


class UTF8Prober(CharSetProber):
    def __init__(self):
        """
        Initialize the character set prober.
        
        This method initializes the character set prober using a coding state machine
        based on the UTF-8 model. It resets the prober to its initial state.
        
        Parameters:
        None
        
        Attributes:
        _mCodingSM (CodingStateMachine): The coding state machine initialized with the UTF-8 model.
        reset (method): Resets the prober to its initial state.
        
        Returns:
        None
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
            if codingState == constants.eError:
                self._mState = constants.eNotMe
                break
            elif codingState == constants.eItsMe:
                self._mState = constants.eFoundIt
                break
            elif codingState == constants.eStart:
                if self._mCodingSM.get_current_charlen() >= 2:
                    self._mNumOfMBChar += 1

        if self.get_state() == constants.eDetecting:
            if self.get_confidence() > constants.SHORTCUT_THRESHOLD:
                self._mState = constants.eFoundIt

        return self.get_state()

    def get_confidence(self):
        """
        get_confidence(self) -> float
        
        This method calculates the confidence level based on the number of multi-byte characters in a text.
        
        Parameters:
        self: The instance of the class containing the _mNumOfMBChar attribute, which represents the number of multi-byte characters in the text.
        
        Returns:
        float: The confidence level, which is a value between 0 and 1. If the number of multi-byte characters is less than 6, the confidence is calculated as 1.0 minus
        """

        unlike = 0.99
        if self._mNumOfMBChar < 6:
            for i in range(0, self._mNumOfMBChar):
                unlike = unlike * ONE_CHAR_PROB
            return 1.0 - unlike
        else:
            return unlike
 unlike
        else:
            return unlike
