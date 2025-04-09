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
        Initializes the character set prober with a UTF-8 coding state machine. Resets the prober's state.
        
        Args:
        None
        
        Attributes:
        _mCodingSM (CodingStateMachine): The coding state machine initialized with the UTF-8 model.
        reset (): Resets the prober's state.
        
        Returns:
        None
        """

        CharSetProber.__init__(self)
        self._mCodingSM = CodingStateMachine(UTF8SMModel)
        self.reset()

    def reset(self):
        """
        Resets the character set prober and the multi-byte character state machine (_mCodingSM). Sets the number of multi-byte characters (_mNumOfMBChar) to 0.
        """

        CharSetProber.reset(self)
        self._mCodingSM.reset()
        self._mNumOfMBChar = 0

    def get_charset_name(self):
        return "utf-8"

    def feed(self, aBuf):
        """
        Feed the buffer `aBuf` into the character decoding process. Update the internal state based on the decoding results. If the decoding state reaches `eItsMe`, set the state to `eFoundIt`. If the confidence exceeds the threshold during detection, also set the state to `eFoundIt`. Return the current state.
        
        Args:
        aBuf (str): The buffer containing characters to be decoded.
        
        Returns:
        int: The current state of the decoder (`eNotMe`,
        """

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
        Calculates the confidence level based on the number of multi-byte characters.
        
        Args:
        self: The instance of the class.
        
        Returns:
        float: The calculated confidence level.
        
        Keyword Arguments:
        _mNumOfMBChar (int): The number of multi-byte characters.
        ONE_CHAR_PROB (float): The probability of a single character.
        
        Summary:
        This function calculates the confidence level by multiplying the probability of a single character (`ONE_CHAR_PROB`) for each multi
        """

        unlike = 0.99
        if self._mNumOfMBChar < 6:
            for i in range(0, self._mNumOfMBChar):
                unlike = unlike * ONE_CHAR_PROB
            return 1.0 - unlike
        else:
            return unlike
