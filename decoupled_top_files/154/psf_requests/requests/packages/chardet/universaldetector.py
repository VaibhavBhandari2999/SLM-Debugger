######################## BEGIN LICENSE BLOCK ########################
# The Original Code is Mozilla Universal charset detector code.
#
# The Initial Developer of the Original Code is
# Netscape Communications Corporation.
# Portions created by the Initial Developer are Copyright (C) 2001
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Mark Pilgrim - port to Python
#   Shy Shalom - original C code
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
import codecs
from .latin1prober import Latin1Prober  # windows-1252
from .mbcsgroupprober import MBCSGroupProber  # multi-byte character sets
from .sbcsgroupprober import SBCSGroupProber  # single-byte character sets
from .escprober import EscCharSetProber  # ISO-2122, etc.
import re

MINIMUM_THRESHOLD = 0.20
ePureAscii = 0
eEscAscii = 1
eHighbyte = 2


class UniversalDetector:
    def __init__(self):
        """
        Initializes the character set detector with regular expression patterns for high-bit characters, escape sequences, and escape character set probers. Resets the internal state.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        _highBitDetector (re.Pattern): Regular expression pattern to detect high-bit characters.
        _escDetector (re.Pattern): Regular expression pattern to detect escape sequences and specific escape characters.
        _mEscCharSetProber (object): Escape character set prober object
        """

        self._highBitDetector = re.compile(b'[\x80-\xFF]')
        self._escDetector = re.compile(b'(\033|~{)')
        self._mEscCharSetProber = None
        self._mCharSetProbers = []
        self.reset()

    def reset(self):
        """
        Resets the character set probers and internal state.
        
        This function resets the result dictionary, sets the done flag to False,
        and resets the internal state variables such as _mStart, _mGotData,
        _mInputState, _mLastChar, _mEscCharSetProber, and CharSetProbers.
        It is used to prepare the object for a new encoding detection process.
        """

        self.result = {'encoding': None, 'confidence': 0.0}
        self.done = False
        self._mStart = True
        self._mGotData = False
        self._mInputState = ePureAscii
        self._mLastChar = b''
        if self._mEscCharSetProber:
            self._mEscCharSetProber.reset()
        for prober in self._mCharSetProbers:
            prober.reset()

    def feed(self, aBuf):
        """
        Determines the character encoding of the given buffer `aBuf`. If the buffer starts with a Byte Order Mark (BOM), it identifies the encoding accordingly. Otherwise, it uses various detectors to identify the encoding, such as high-byte detector and escape character set prober. The function updates the internal state based on the detected encoding and returns the result as a dictionary containing the identified encoding and its confidence level. If the encoding is found, the function sets the `done` flag to True.
        """

        if self.done:
            return

        aLen = len(aBuf)
        if not aLen:
            return

        if not self._mGotData:
            # If the data starts with BOM, we know it is UTF
            if aBuf[:3] == codecs.BOM_UTF8:
                # EF BB BF  UTF-8 with BOM
                self.result = {'encoding': "UTF-8-SIG", 'confidence': 1.0}
            elif aBuf[:4] == codecs.BOM_UTF32_LE:
                # FF FE 00 00  UTF-32, little-endian BOM
                self.result = {'encoding': "UTF-32LE", 'confidence': 1.0}
            elif aBuf[:4] == codecs.BOM_UTF32_BE:
                # 00 00 FE FF  UTF-32, big-endian BOM
                self.result = {'encoding': "UTF-32BE", 'confidence': 1.0}
            elif aBuf[:4] == b'\xFE\xFF\x00\x00':
                # FE FF 00 00  UCS-4, unusual octet order BOM (3412)
                self.result = {
                    'encoding': "X-ISO-10646-UCS-4-3412",
                    'confidence': 1.0
                }
            elif aBuf[:4] == b'\x00\x00\xFF\xFE':
                # 00 00 FF FE  UCS-4, unusual octet order BOM (2143)
                self.result = {
                    'encoding': "X-ISO-10646-UCS-4-2143",
                    'confidence': 1.0
                }
            elif aBuf[:2] == codecs.BOM_LE:
                # FF FE  UTF-16, little endian BOM
                self.result = {'encoding': "UTF-16LE", 'confidence': 1.0}
            elif aBuf[:2] == codecs.BOM_BE:
                # FE FF  UTF-16, big endian BOM
                self.result = {'encoding': "UTF-16BE", 'confidence': 1.0}

        self._mGotData = True
        if self.result['encoding'] and (self.result['confidence'] > 0.0):
            self.done = True
            return

        if self._mInputState == ePureAscii:
            if self._highBitDetector.search(aBuf):
                self._mInputState = eHighbyte
            elif ((self._mInputState == ePureAscii) and
                    self._escDetector.search(self._mLastChar + aBuf)):
                self._mInputState = eEscAscii

        self._mLastChar = aBuf[-1:]

        if self._mInputState == eEscAscii:
            if not self._mEscCharSetProber:
                self._mEscCharSetProber = EscCharSetProber()
            if self._mEscCharSetProber.feed(aBuf) == constants.eFoundIt:
                self.result = {'encoding': self._mEscCharSetProber.get_charset_name(),
                               'confidence': self._mEscCharSetProber.get_confidence()}
                self.done = True
        elif self._mInputState == eHighbyte:
            if not self._mCharSetProbers:
                self._mCharSetProbers = [MBCSGroupProber(), SBCSGroupProber(),
                                         Latin1Prober()]
            for prober in self._mCharSetProbers:
                if prober.feed(aBuf) == constants.eFoundIt:
                    self.result = {'encoding': prober.get_charset_name(),
                                   'confidence': prober.get_confidence()}
                    self.done = True
                    break

    def close(self):
        """
        Closes the encoding detector, setting the `done` flag to True. If no data was received or the input state is in pure ASCII, returns the result with encoding set to 'ascii' and confidence set to 1.0. Otherwise, it evaluates the confidence of each charset prober and selects the one with the highest confidence above a certain threshold. If such a prober exists, sets the result with the detected encoding and its confidence. If no prober meets the threshold, logs a
        """

        if self.done:
            return
        if not self._mGotData:
            if constants._debug:
                sys.stderr.write('no data received!\n')
            return
        self.done = True

        if self._mInputState == ePureAscii:
            self.result = {'encoding': 'ascii', 'confidence': 1.0}
            return self.result

        if self._mInputState == eHighbyte:
            proberConfidence = None
            maxProberConfidence = 0.0
            maxProber = None
            for prober in self._mCharSetProbers:
                if not prober:
                    continue
                proberConfidence = prober.get_confidence()
                if proberConfidence > maxProberConfidence:
                    maxProberConfidence = proberConfidence
                    maxProber = prober
            if maxProber and (maxProberConfidence > MINIMUM_THRESHOLD):
                self.result = {'encoding': maxProber.get_charset_name(),
                               'confidence': maxProber.get_confidence()}
                return self.result

        if constants._debug:
            sys.stderr.write('no probers hit minimum threshhold\n')
            for prober in self._mCharSetProbers[0].mProbers:
                if not prober:
                    continue
                sys.stderr.write('%s confidence = %s\n' %
                                 (prober.get_charset_name(),
                                  prober.get_confidence()))
