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
        CharSetProber.__init__(self)
        self._mCodingSM = [
            CodingStateMachine(HZSMModel),
            CodingStateMachine(ISO2022CNSMModel),
            CodingStateMachine(ISO2022JPSMModel),
            CodingStateMachine(ISO2022KRSMModel)
        ]
        self.reset()

    def reset(self):
        """
        Reset the state of the CharSetProber.
        
        This method resets the state of the CharSetProber to its initial condition, preparing it for a new encoding detection process. It iterates through all coding state machines (SM) and resets them, setting their 'active' flag to True. The method also resets the count of active state machines and clears the detected character set.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        _mCodingSM (list): A list of coding state machines
        """

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
        self (object): The object instance that contains the `_mDetectedCharset` attribute.
        
        Returns:
        float: The confidence level of the detected character set. Returns 0.99 if a charset is detected, otherwise returns 0.00.
        
        This function checks whether a charset has been detected and returns a confidence level based on that detection.
        """

        if self._mDetectedCharset:
            return 0.99
        else:
            return 0.00

    def feed(self, aBuf):
        """
        Feed a buffer of bytes to the charset detector.
        
        Parameters:
        aBuf (bytes): A buffer of bytes to be processed.
        
        Returns:
        int: The current state of the charset detector after processing the buffer.
        
        This function processes a buffer of bytes, updating the state of the charset detector based on the encoding states. It iterates through each byte in the buffer, updating the state machines for each active coding state. If an error state is reached, the corresponding state machine is deactivated. If all
        """

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
