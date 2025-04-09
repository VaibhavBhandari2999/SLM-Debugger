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

from . import constants
import sys
from .charsetprober import CharSetProber


class CharSetGroupProber(CharSetProber):
    def __init__(self):
        """
        Initializes the CharSetProber object. Sets up the active number of probers, initializes an empty list of probers, and sets the best guess prober to None.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        _mActiveNum (int): The number of active probers.
        _mProbers (list): A list of probers.
        _mBestGuessProber (CharSetProber): The best guess prober for character set
        """

        CharSetProber.__init__(self)
        self._mActiveNum = 0
        self._mProbers = []
        self._mBestGuessProber = None

    def reset(self):
        """
        Resets the character set prober.
        
        This method resets the internal state of the character set prober,
        including the active number of probers and their individual states.
        It also sets the best guess prober to None.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes Affected:
        - _mActiveNum: The number of active probers.
        - _mProbers: A list of character set probers.
        - _mBest
        """

        CharSetProber.reset(self)
        self._mActiveNum = 0
        for prober in self._mProbers:
            if prober:
                prober.reset()
                prober.active = True
                self._mActiveNum += 1
        self._mBestGuessProber = None

    def get_charset_name(self):
        """
        Gets the character set name based on the best guess prober.
        
        This method retrieves the character set name using the best guess prober. If no best guess prober is available, it first calls `get_confidence` to initialize one. If initialization fails, it returns `None`. Otherwise, it returns the character set name from the best guess prober.
        
        Args:
        None
        
        Returns:
        str or None: The character set name if available, otherwise `None`.
        """

        if not self._mBestGuessProber:
            self.get_confidence()
            if not self._mBestGuessProber:
                return None
#                self._mBestGuessProber = self._mProbers[0]
        return self._mBestGuessProber.get_charset_name()

    def feed(self, aBuf):
        """
        Feed data buffer (aBuf) to character encoding probers to determine the encoding of the input text. This method iterates through each active prober, feeds the buffer to it, and updates the best guess prober if an encoding is detected. If no encoding is found, it returns the current state of the object.
        
        Args:
        aBuf (bytes): Input data buffer to be analyzed.
        
        Returns:
        dict: Current state of the object or the state indicating that no encoding was
        """

        for prober in self._mProbers:
            if not prober:
                continue
            if not prober.active:
                continue
            st = prober.feed(aBuf)
            if not st:
                continue
            if st == constants.eFoundIt:
                self._mBestGuessProber = prober
                return self.get_state()
            elif st == constants.eNotMe:
                prober.active = False
                self._mActiveNum -= 1
                if self._mActiveNum <= 0:
                    self._mState = constants.eNotMe
                    return self.get_state()
        return self.get_state()

    def get_confidence(self):
        """
        Get the confidence of the current state.
        
        Args:
        None
        
        Returns:
        float: The confidence value based on the current state or the best guess prober's confidence.
        
        Summary:
        This function determines the confidence level based on the current state. If the state is 'eFoundIt', it returns 0.99. If the state is 'eNotMe', it returns 0.01. Otherwise, it iterates through all active probers, finds the
        """

        st = self.get_state()
        if st == constants.eFoundIt:
            return 0.99
        elif st == constants.eNotMe:
            return 0.01
        bestConf = 0.0
        self._mBestGuessProber = None
        for prober in self._mProbers:
            if not prober:
                continue
            if not prober.active:
                if constants._debug:
                    sys.stderr.write(prober.get_charset_name()
                                     + ' not active\n')
                continue
            cf = prober.get_confidence()
            if constants._debug:
                sys.stderr.write('%s confidence = %s\n' %
                                 (prober.get_charset_name(), cf))
            if bestConf < cf:
                bestConf = cf
                self._mBestGuessProber = prober
        if not self._mBestGuessProber:
            return 0.0
        return bestConf
#        else:
#            self._mBestGuessProber = self._mProbers[0]
#            return self._mBestGuessProber.get_confidence()
