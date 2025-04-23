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
from .escsm import (HZSMModel, ISO2022CNSMModel, ISO2022JPSMModel,
                    ISO2022KRSMModel)
from .charsetprober import CharSetProber
from .codingstatemachine import CodingStateMachine
from .compat import wrap_ord


class EscCharSetProber(CharSetProber):
    def __init__(self):
        """
        Initialize the character set prober.
        
        This method sets up the character set prober with different coding state machines for handling different character encoding models. It initializes the prober and resets its state.
        
        Parameters:
        None
        
        Attributes:
        _mCodingSM (list): A list of coding state machines for handling different character encoding models.
        reset (method): Resets the prober to its initial state.
        
        Models:
        HZSMModel: Model for handling HZ (Chinese) character encoding.
        """

        CharSetProber.__init__(self)
        self._mCodingSM = [
            CodingStateMachine(HZSMModel),
            CodingStateMachine(ISO2022CNSMModel),
            CodingStateMachine(ISO2022JPSMModel),
            CodingStateMachine(ISO2022KRSMModel)
        ]
        self.reset()

    def reset(self):
        CharSetProber.reset(self)
        for codingSM in self._mCodingSM:
            if not codingSM:
                continue
            codingSM.active = True
            codingSM.reset()
        self._mActiveSM = len(self._mCodingSM)
        self._mDetectedCharset = None

    def get_charset_name(self):
        return self._mDetectedCharset

    def get_confidence(self):
        """
        Function to determine the confidence level of the detected character set.
        
        Parameters:
        self (object): The instance of the class containing the method.
        
        Returns:
        float: The confidence level of the detected character set. Returns 0.99 if a charset is detected, otherwise returns 0.00.
        
        This method checks if a charset has been detected and returns a confidence level based on the detection status.
        """

        if self._mDetectedCharset:
            return 0.99
        else:
            return 0.00

    def feed(self, aBuf):
        for c in aBuf:
            # PY3K: aBuf is a byte array, so c is an int, not a byte
            for codingSM in self._mCodingSM:
                if not codingSM:
                    continue
                if not codingSM.active:
                    continue
                codingState = codingSM.next_state(wrap_ord(c))
                if codingState == constants.eError:
                    codingSM.active = False
                    self._mActiveSM -= 1
                    if self._mActiveSM <= 0:
                        self._mState = constants.eNotMe
                        return self.get_state()
                elif codingState == constants.eItsMe:
                    self._mState = constants.eFoundIt
                    self._mDetectedCharset = codingSM.get_coding_state_machine()  # nopep8
                    return self.get_state()

        return self.get_state()
state()
  return self.get_state()

        return self.get_state()
state()
