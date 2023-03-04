#!/usr/local/python3

# This code was developed for MacOS but should work under Windows and Linux

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public 
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, 
# see <https://www.gnu.org/licenses/>.

# Having said that, it would be great to know if this software gets used. If you want, buy me a coffee, or send me some hardware
# Darryl Smith, VK2TDS. darryl@radio-active.net.au Copyright 2023



#https://pynput.readthedocs.io/en/latest/keyboard.html ????????
#http://pymotw.com/2/readline/ ??????



# TNC2 Commands
# https://web.tapr.org/meetings/CNC_1986/CNC1986-TNC-2Setting-W2VY.pdf

import string
from types import SimpleNamespace
import re
import eliza # for testing
from datetime import timezone
import datetime
import gnureadline as readline

streamlist = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')


returns = SimpleNamespace(**{'Ok':0, 'Eh': 1, 'Bad': 2, 'NotImplemented': 3})


TNC2_ROM = {
    'Help': {'Commands': ['All'], 'Help':'Get help on commands'},
    '8bitconv': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Strip high-order bit when in convers mode'},
    'ANSWRQRA': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Setting ANSWRQRA  to OFF  disables the TNC\'s  ping-response function'},
    'ACKPRIOR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'When ACKPRIOR is  ON, acknowledgments have priority'},
    'ADRdisp': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Address headers on monitored frames will be displayed.'},
    'AMonth': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Display months as words'},
    'AUtolf': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Send Linefeed to terminal after each CR'},
    'AWlen': {'Commands': [7, 8], 'Group': 'A',  'Default': '7', 'Min': 7, 'Max': 8, 'Help': 'Terminal character length (7/8)'},
    'Ax2512v2': {'Commands': ['On', 'Off'], 'Group': 'L',  'Default': 'Off', 'Help': 'Run as version 1.0 of AX.25'},
    'AXDelay': {'Commands': [], 'Group': 'T', 'Default': '0', 'Min': 0, 'Max': 180, 'Help': '(O-180 * 0.1 set) Voice Repeater keyup delay'},
    'AXHang': {'Commands': [], 'Group': 'T',  'Default': '0', 'Min': 0, 'Max': 20, 'Help': '(O-20 * 0.1 set) Voice Repeater hang time'},
    'ACKTIME': {'Commands': [], 'Group': 'T', 'Default': '14', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 mSec) ACKTIME specifies the time required to send an RR or RNR response frame'},
    'Beacon': {'Commands': ['Every', 'After'], 'Group': 'I', 'Minimum': 2, 'Default': 'Every 0', 'Help': 'Every/After O-250 *lO sec'},
    'BBSMSGS': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'This  command controls how  the TNC displays  certain messages in COMMAND and CONVERSE  modes'},
    'BKondel': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'On', 'Help': 'Send BS SP BS for each DELETE character'},
    'BText': {'Commands': [], 'Group': 'I', 'Default': 'Beacon Text', 'Minimum': -1, 'Help': '(120 char) Text to be sent for a beacon)'},
    'BUdlist': {'Commands': ['On', 'Off'], 'Group': 'M',  'Default': 'Off', 'Help': 'Stations in Lcalls are ignored'},
    'CALibra': {'Commands': [], 'Help': 'Used to calibrate the builtin modem'},
    'CALSet' : {'Commands': [], 'Group': 'T', 'Help': 'Used with CALibrate'},
    'CANline': {'Commands': [], 'Group': 'C', 'Default': '$18', 'Help': '(Control-X) The Line Delete character'},
    'CANPac': {'Commands': [], 'Group': 'C', 'Default': '$19', 'Help': '(Ctrl-Y) Cancel current character'},
    'CHeck': {'Commands': [], 'Group': 'T', 'Default': '30', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 set) Idle link time out'},
    'CLKADJ': {'Commands': [], 'Group': 'T', 'Default': '0', 'Min': 0, 'Max': 65536, 'Help': '(O-65535) Real time clock adjustment constant'},
    'CMDtime': {'Commands': [], 'Group': 'T', 'Default': '1', 'Min': 0, 'Max': 255, 'Help': '(O-255 set) transparent mode escape timer'},
    'CMSG': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Don\'t send CTEXT when user links to your TNC'},
    'CBELL': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Ring a bell on Connect'},
    'COMmand': {'Commands': [], 'Group': 'C', 'Default': '$03', 'Help': 'Char to escape from CONVERS mode to command mode'},
    'CONMode': {'Commands': ['Convers', 'Trans'], 'Group': 'L', 'Default': 'Convers', 'Help': 'Mode to enter when link established'},
    'Connect': {'Commands': [], 'Help': 'Establish Link with station via optional stations. CONNECT VK2TDS-1 Via VK2TDS-2, VL2TDS-3 VK2TDS-4'},
    'CONOk': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Allow stations to establish a link with your TNC'},
    'CONPerm': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'If ON always keep this link up (never Disconnect)'},
    'CONStamp': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'If ON print date & time stamp on connect messages'},
    'CHECKV1': {'Commands': ['On', 'Off'], 'Group': 'T', 'Default': 'Off', 'Help': 'Enables  CHECKtime  (T3)  when running  AX.25  Level  2 Version 1.0 protocol.'},
    'CStatus':  {'Commands': [], 'Help': 'Prints the status of all links (Streams)'},
    'CONVers': {'Commands': [], 'Help': 'Enter Converse mode from command mode'},
    'CMSGDISC': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Automatic disconnect'},
    'CPactime': {'Commands': ['On', 'Off'], 'Group': 'T', 'Default': 'Off', 'Help': 'Don\'t forward data based on timers (see Pactime)'},
    'CR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Append a Carriage Return to each data packet'},
    'CText': {'Commands': [], 'Group': 'I',  'Default': '%', 'Minimum': -1, 'Help': '(120 Ch) Connect Message Text (see CMSG)'},
    'DAytime': {'Commands': [], 'Help': 'Date and time for real time clock'},
    'DAYUsa': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Print date as mm/dd/yy instead of dd-mm-yy'},
    'DELete': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'Off', 'Help': 'The character delete is BS ($08) not DEL ($7E)'},
    'DIGipeat': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Allow stations to use you as a Digipeater'},
    'Disconne': {'Commands': [], 'Help': 'Request a link disconnect from the other station'},
    'DEADTIME': {'Commands': [], 'Group': 'T', 'Default': '33', 'Min': 0, 'Max': 250, 'Help': '0-250 * 10mSec specifies the  time it  takes a  station\'s receiver  todetect the  fact that  a remote  transmitter  has keyed  up'},
    'Display': {'Commands': ['Async',                # 
                'Character', 
                'Health', 
                'Id',
                'Link',
                'Monitor',
                'Timing'], 'Help': '(Async/Character/Id/Monitor/Timing) Parameters'},
    'DWait': {'Commands': [], 'Group': 'T', 'Default': '16', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 msec) Delay to let digipeater repeat'},
    'Echo': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Echo characters typed on keyboard to terminal'},
    'Escape': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Don\'t translate ES@ character ($lB) to $ ($24:)'},
    'Flow': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Don\'t print to terminal while user is typing'},
    'FIRMRNR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'When this TNC\'s buffers fill, an RNR is sent'},
    'FSCreen': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Display command generates 4 columns - default ON'},
    'FRack': {'Commands': [], 'Group': 'T', 'Default': '3', 'Min': 1, 'Max': 15, 'Help': '(l-15 set) Time needed to ack a packet per station'},
    'FUlldup': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Operate in Simplex mode'},
    'HEaderln': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Print the frame header and text on the same line'},
    'HID': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Don\'t send an ID packet every 9.5 mins when active'},
    'ID': {'Commands': [], 'Help': 'Force an ID packet (UI frame Via UNproto path)'},
    'LCALLS': {'Commands': [], 'Group': 'M', 'Default': '%', 'Minimum': -1, 'Help': '(O-8 calls) to receive or ignore stations (BUDLIST)'},
    'LCok': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Do not convert lower case to UPPER CASE on terminal'},
    'LCSTREAM': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'On', 'Help': 'Convert the stream select specifer to Upper case'},
    'LFIGNORE': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'TNC will ignore <LF> characters'},
    'LFadd': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Add a Line Feed after each CR send to the terminal'},
    'KISSdev': {'Commands': [], 'Group': 'M', 'Default': 'KISSdev 1  tcp localhost 8001', 'Minimum': -1, 'Help': 'Open a KISS Device in aioax25. First number is the Kiss Device number'},
    'KISSPort': {'Commands': [], 'Group': 'M', 'Default': 'KISSport 1 1', 'Minimum': -1, 'Help': 'Definces the Kissport for a device. First number is device number and then port number'},
    'MAll': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Monitor data frames as well as beacons'},
    'MAXframe': {'Commands': [], 'Group': 'L', 'Default': '4', 'Min': 1, 'Max': 7, 'Help': 'The window size for outstanding frames'},
    'MCOM': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Monitor only data frames instead of all types'},
    'MCon': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Don\'t monitor frames when linked to another station'},
    'MRpt': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Dont show monitored intermediate stations when off'},
    'MNONAX25': {'Commands': ['On', 'Off'], 'Group': 'N', 'Default': 'Off', 'Help': 'Monitors  AX.25  Level   2  Protocol  frames  with   no higher-level protocols (PID = F0)'},
    'MFilter': {'Commands': [], 'Group': 'I', 'Minimum': -1, 'Help': 'Up to 4 characters to be removed from monitored data with commas'},
    'MHClear': {'Commands': [], 'Help': 'Clear the calls Heard list'},
    'MHeard': {'Commands': [], 'Help': 'Display the calls heard and date/time if clock set'},
    'Monitor': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Monitor mode on - see BUDLIST, MALL, MCON, MSTAMP'},
    'MTRans': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Monitoring is enabled when in Transparent mode.'},
    'MRpt': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Display the digipeater path in monitored frames'},
    'MStamp': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Monitored frames are Not time stamped'},
    'MYALIAScall': {'Commands': [], 'Group': 'I', 'Minimum': -1, 'Help': 'An identifier for a digipeater'},
    'MYcall': {'Commands': [], 'Group': 'I', 'Default': 'N0CALL-0', 'Help': 'The station callsign for ID and linking'},
    'NEwmode': {'Commands': ['On', 'Off'], 'Group': 'L',  'Default': 'Off', 'Help': 'The TNC acts like a TNC I for changing modes'},
    'NOmode': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'If ON allow explicit mode change only'},
    'NUcr': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Don\'t send NULLS ($00) after a CR'},
    'NULf': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Don\'t send Nulls after a LF'},
    'NULLS': {'Commands': [], 'Group': 'A', 'Default': '0', 'Min': 0, 'Max': 30, 'Help': '(O-30) Number of nulls to send as requested'},
    'Paclen': {'Commands': [], 'Group': 'L', 'Default': '128', 'Min': 0, 'Max': 255, 'Help': '(O-255,0=256) size of the data field in a data frame'},
    'PACTime': {'Commands': ['Every', 'After'], 'Group': 'T', 'Minimum': 2, 'Default': 'After 10', 'Help': '(Every/After O-250 *lOO ms) Data forwarding timer'},
    'PARity': {'Commands': [0,1,2,3], 'Group': 'A', 'Default': '3', 'Min': 0, 'Max': 3, 'Help': '(O-3) Terminal parity 0,2=None l=odd 3=even'},
    'PASs': {'Commands': [], 'Group': 'C', 'Default': '$16', 'Help': '(CTRL-V) char to allow any character to be typed'},
    'PASSAll': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Accept only frames with valid CRCs'},
    'RXBLOCK': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'The  TNC will  send  data to  the  terminal in  RXBLOCK format.'},
    'RECOnnect': {'Commands': [], 'Help': 'Like Connect but to restablish a link via a new path'},
    'REDisplay': {'Commands': [], 'Group': 'C', 'Default': '$12', 'Help': '(CTRL-R) char to print the current input buffer'},
    'RESET': {'Commands': [], 'Help': 'RESET bbRAM PARAMETERS TO DEFAULTS'},
    'RESptime': {'Commands': [], 'Group': 'T', 'Default': '12', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 100 ms) minimum delay for sending an ACK'},
    'RESTART': {'Commands': [], 'Help': 'Perform a power on reset'},
    'RETry': {'Commands': [], 'Group': 'L', 'Default': '10', 'Min': 0, 'Max': 15, 'Help': '(O-15) maximum number of retries for a frame'},
    'Screenln': {'Commands': [], 'Group': 'A', 'Default': '80', 'Min': 0, 'Max': 255, 'Help': '(O-255) Terminal output width'},
    'SLOTS': {'Commands': [], 'Group': 'L', 'Default': '3', 'Min': 0, 'Max': 127, 'Help': '(O-127) specifies the number  of "slots" from which to  choose when deciding to access the channel'},
    'SEndpac': {'Commands': [], 'Group': 'C', 'Default': '$0D', 'Help': '(CR) Char to force a frame to be sent)'},
    'STArt': {'Commands': [], 'Group': 'C', 'Default': '$11', 'Help': '(CTRL-Q) the XON for data TO the terminal'},
    'STOp': {'Commands': [], 'Group': 'C', 'Default': '$13', 'Help': '(CTRL-S) the XOFF for data TO the terminal'},
    'STREAMCa': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'Off', 'Help': 'Don\'t show the callsign after stream id'},
    'STREAMDbl': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'Off', 'Help': 'Don\'t print the stream switch char twice (!!A)'},
    'STReamsw': {'Commands': [], 'Group': 'C', 'Default': '$7c', 'Help': 'Character to use to change streams (links)'},
    'TRAce': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Hexidecimal trace mode is disabled'},
    'TRANS': {'Commands': [], 'Help': 'The TNC enters Transparent data mode'},
    'STATUS': {'Commands': [], 'Help': 'It  returns the  acknowledged status  of the  current  outgoing packet  link  buffer.'},
    'TRFlow': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Disable flow control to the Terminal (Trans mode)'},
    'TRIes': {'Commands': [], 'Group': 'L', 'Min': 0, 'Max': 15,  'Help': '(O-15) set or display the current retry counter'},
    'TXdelay': {'Commands': [], 'Group': 'T', 'Default': '30', 'Min': 0, 'Max': 120, 'Help': '(O-120 * 10ms) Keyup delay for the transmitter'},
    'TXDELAYC': {'Commands': [], 'Group': 'T', 'Default': '2', 'Min': 0, 'Max': 120, 'Help': 'specifying  additional transmit  delay time added to TXdelay in terms of CHARACTER TIME at the current radio port data rate.'},
    'TXFlow': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Disable flow control to the TNC (Transparent mode)'},
    'TXDIDDLE': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'TXDIDDLE should be kept ON  unless you  are  certain the  TNCs  in your  network  require lengthy flagging intervals.'},
    'TXUIFRAM': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'The TNC will "flush its buffers" to the radio port upon loss of a connection.'},
    'Unproto': {'Commands': [], 'Group': 'I', 'Default': 'CQ','Minimum': -1, 'Help': 'Path and address to send beacon data'},
    'Users': {'Commands': [], 'Group': 'L', 'Default': '1', 'Min': 1, 'Max': 16, 'Help': 'Sets the number of streams (links) allowed'},
    'Xflow': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'XON/XOFF Flow control enabled instead of hardware'},
    'XMitok': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Allow transmitter to come on'},
    'UTC': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Display times in UTC'},
    'XOff': {'Commands': [], 'Group': 'C', 'Default': '$13', 'Help': '(CTRL-S) Character to stop data from terminal'},
    'XON': {'Commands': [], 'Group': 'C', 'Default': '$11', 'Help': '(CTRL-Q) Character to start data from terminal'},
}


class BufferAwareCompleter:

    def __init__(self, options, logging):
        self.options = options
        self.current_candidates = []
        self.logging = logging 


    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.

            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            self.logging.debug('origline=%s', repr(origline))
            self.logging.debug('begin=%s', begin)
            self.logging.debug('end=%s', end)
            self.logging.debug('being_completed=%s', being_completed)
            self.logging.debug('words=%s', words)

            if not words:
                self.current_candidates = sorted(
                    self.options.keys()
                )
            else:
                try:
                    if begin == 0:
                        # first word
                        #candidates = self.options.keys()
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        #logging.debug (first)
                        c = self.options[first.upper()]['Commands']
                        #logging.debug (c)
                        candidates = [x.upper() for x in c]
                        #logging.debug('Xcandidates=%s',
                        #          c)
                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [
                            w for w in candidates
                            if w.upper().startswith(being_completed.upper())
                            #if w.startswith(being_completed)
                        ]
                    else:
                        # matching empty string,
                        # use all candidates
                        self.current_candidates = candidates

                    self.logging.debug('candidates=%s',
                                  self.current_candidates)

                except (KeyError, IndexError) as err:
                    self.logging.error('completion error: %s', err)
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        self.logging.debug('complete(%s, %s) => %s',
                      repr(text), state, response)
        return response





class connection:

    def __init__ (self, callFrom, callTo, callDigi, stream):
        self.callFrom = callFrom
        self.callTo = callTo
        self.callDigi = callDigi
        self.therapist = None
        self.connectedSession = False
        self.stream = stream
        self.stream['Connection'] = self

        print ('Manage a connection from %s to %s via %s' % (callFrom, callTo, callDigi))
        if self.stream['axInit']:
            for callback in self.stream['axInit']:
                callback (self.stream['Stream'])
        if self.stream['cbInit']:
            for callback in self.stream['cbInit']:
                callback (self.stream['Stream'])


    def connect(self):
        print ('connection connect')
        self.axConnected = True
        #if self.stream['cbInit']:
        #    for callback in self.stream['cbInit']:
        #        callback (self.stream['Stream'])

    def disconnect(self):
        self.axConnected = False

    @property
    def axConnected(self):
        return self.connectedSession
    
    @axConnected.setter
    def axConnected(self, status):
        # Shouldnt use this function
        self.connectedSession = status
        if status == True:
            if self.stream['axConnect']:
                for callback in self.stream['axConnect']:
                    callback (self.stream['Stream'])
            if self.stream['cbConnect']:
                for callback in self.stream['cbConnect']:
                    callback (self.stream['Stream'])
        elif status == False:
            if self.stream['axDisconnect']:
                for callback in self.stream['axDisconnect']:
                    callback (self.stream['Stream'])
            if self.stream['cbDisconnect']:
                for callback in self.stream['cbDisconnect']:
                    callback (self.stream['Stream'])
            self.callFrom = None
            self.callTo = None
            self.callDigi = None

    def axSend(self, text):
        print ('axSend %s' % (text))
        if self.stream['axSent']:
            for callback in self.stream['axSent']:
                callback (text, self.stream['Stream'])
        if self.stream['cbSent']:
            for callback in self.stream['cbSent']:
                callback (text, self.stream['Stream'])

    def axReceived (self, text):
        if self.stream['axReceived']:
            for callback in self.stream['axReceived']:
                callback (text, self.stream['Stream'])
        if self.stream['cbReceived']:
            for callback in self.stream['cbReceived']:
                callback (text, self.stream['Stream'])



def is_hex(s):
     hex_digits = set(string.hexdigits)
     # if s is long, then it is faster to check against a set
     return all(c in hex_digits for c in s)


def to_user (command, old, new):
    if old is None:
        if new is True:
            new = 'On'
        if new is False:
            new = 'Off'
        return ('%s%s' % (command.ljust(13), str(new).ljust(10)))
    else:
        # old is NOT None
        if new is True:
            new = 'On'
        if new is False:
            new = 'Off'
        if old is True:
            old = 'On'
        if old is False:
            old = 'Off'
        return ('%s was %s' % (command, old))





class process:
    # Process commands
    def __init__ (self, completer, tnc):
        self.completer = completer
        self.tnc = tnc


    def displaydatetime (self, dt):
        if self.completer.options['DAYUSA']['Value']:
            if self.completer.options['AMONTH']['Value']:
                return dt.strftime ('%d-%b-%Y %H:%M:%S')
            else:
                return dt.strftime ('%m/%d/%Y %H:%M:%S')
        else:
            if self.completer.options['AMONTH']['Value']:
                return dt.strftime ('%d-%b-%Y %H:%M:%S')
            else:
                return dt.strftime ('%d/%m/%Y %H:%M:%S')


    def input_cleanup (self, words):
        # Upper case the first word
        words [0] = words[0].upper()
        if words[0] == 'K':
            words[0] = 'CONNECT'
        if not words[0] in self.completer.options:
            # didnt find the first word, so see if we can do a shorter version
            for o in self.completer.options:
                if self.completer.options[o]['Shorter'] == words[0]:
                    words[0] = o
        if not words[0] in self.completer.options:
            #ToDo: Remove one character at a time to see if there is a match            
            True

        if len(words) == 1:
            return words

        # We have more than one word
        if words[0] in self.completer.options:
            c = self.completer.options[words[0]]['Commands']
            if words[1].capitalize() in c:
                words[1] = words[1].capitalize()
            if not words[1].capitalize() in c:
                if len(c) > 0:
                    if 'On' in c and 'Off' in c:
                        words[1] = words[1].capitalize()
                        if words[1] == 'Yes':
                            words[1] = 'On'
                        if words[1] == 'No':
                            words[1] = 'Off'
            if not words[1].capitalize() in c:
                # if we cannot find it in the list, see if we can find the first capital letters
                # ToDo: Trim words[0] to the length of the upper case letters 
                for w in c:
                    if words[1].capitalize() == ''.join(filter(str.isupper, str(w))):
                        words[1] = w

        if words[0] == 'CONNECT' or words[0] == 'RECONNECT':
            if len(words) > 3:
                words[2] = words[2].upper()
                if words[2] == 'VIA' or words[2] == 'V':
                    words[2] = 'VIA'

        return words


    def input_process (self, line, display=True):
        
        words = line.split()
        if len(words) == 0:
            return returns.Ok

        words = self.input_cleanup (words)

        if words[0][0:4] == '/OPT':
            # Oops. We are in Visual Studio Code and tried to run and are already running!
            exit()
            return returns.NotImplemented

        if False:
            True
        elif words[0] == 'HELP':
            if len(words) == 1:
                if display == True: output (self.completer.options['HELP']['Help'])
                return returns.Ok
            if len(words) >= 2:
                if words[1].upper() == 'ALL':
                    for uc in self.completer.options:
                        if 'Help' in self.completer.options[uc]:
                            if display == True: output ('%s\t%s' % (uc, self.completer.options[uc]['Help']))
                    return returns.Ok
                if words[1] in self.completer.options:
                    uc = words[1].upper()
                    if 'Help' in self.completer.options[uc]:
                        if display == True: output (self.completer.options[uc]['Help'])
                        return returns.Ok
                    else:
                        if display == True: output ('No help available')
                        return returns.Ok
            return returns.Bad
        elif words[0] == 'DISPLAY':
            if len(words) == 1:
                cols = 0
                message = ''
                for o in self.completer.options:
                    if 'Value' in self.completer.options[o]:
                                if len(message) > 0:
                                    message = message + '\t\t' + to_user (o, None, self.completer.options[o]['Value'])
                                else:
                                    message = to_user (o, None, self.completer.options[o]['Value'])
                                cols += 1
                                if 'FSCREEN' in self.completer.options:
                                    if not self.completer.options['FSCREEN']['Value']:
                                        # If we are not in FSCREEN, we only want one column
                                        cols = 4
                                if cols == 4:
                                    if display: output (message)
                                    cols = 0
                                    message = ''
                                        
                return returns.Ok
            if len(words) > 1:
                group = words[1][0]
                cols = 0
                message = ''
                for o in self.completer.options:
                    if 'Group' in self.completer.options[o]:
                        if self.completer.options[o]['Group'] == group: 
                            if 'Value' in self.completer.options[o]:
                                if len(message) > 0:
                                    message = message + '\t\t' + to_user (o, None, self.completer.options[o]['Value'])
                                else:
                                    message = to_user (o, None, self.completer.options[o]['Value'])
                                cols += 1
                                if 'FSCREEN' in self.completer.options:
                                    if not self.completer.options['FSCREEN']['Value']:
                                        # If we are not in FSCREEN, we only want one column
                                        cols = 4
                                if cols == 4:
                                    if display == True: 
                                        print (message)
                                        cols = 0
                                        message = ''

                return returns.Ok
            return returns.Bad
        elif words[0] == 'LCALLS':
            # special case - blank with %
            if len(words) > 1:
                self.completer.options['LCALLS']['Value'] = ''
                return returns.Ok
            else:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['LCALLS']['Value'] = ''
                    return returns.Ok
        elif words[0] == 'CTEXT':
            # special case - blank with %
            if len(words) > 1:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['CTEXT']['Value'] = ''
                    return returns.Ok
        elif words[0] == 'CONNECT':
            if len(words) < 2:
                return returns.Bad
            # put the words back together and then split them with space and commas
            words = " ".join(words).upper()
            calls = re.split (r"[ ,]", words)
            calls = [value for value in calls if value != '']
            callFrom = self.completer.options['MYCALL']['Value']
            callTo = calls[1]
            callDigi = []
            if len(calls) > 2:
                if calls[2] == 'VIA':
                    callDigi = calls[3:]
                else:
                    # The third word *MUST* be 'VIA' of there are digipeaters
                    return returns.Eh    
                if len(calls) == 3:
                    # We need digipeaters if there is a 'Via'
                    return returns.Eh    
            #self.tnc.streams['A']['Connection'] = 
            connection (callFrom, callTo, callDigi, self.tnc.streams['A'])
            self.tnc.streams['A']['Connection'].connect()
            return returns.Ok
        elif words[0] == 'KISSDEV':
            # KISSdev 1 tcp localhost 8001
            if len(words) == 5 and not self.tnc.kiss_interface is None:
                print (words[2].upper())
                if words[2].upper() == 'TCP':
                    self.tnc.kiss_interface.kissDeviceTCP (int (words[1]), words[3], int (words[4]))
                    return returns.Ok
                else: 
                    return returns.Eh    
            else: 
                return returns.Eh
        elif words[0] == 'KISSPORT':
            # KISSport 1 1
            if len(words) == 3 and not self.tnc.kiss_interface is None:
                print ('Port')
                self.tnc.kiss_interface.kissPort (int (words[1]), int (words[2]))
                return returns.Ok
            else:
                return returns.Eh
        elif words[0] == 'RECONNECT':
            return returns.NotImplemented


        if len(words) == 1 and words[0].upper() in self.completer.options:        # If a single word only, and it has a value,
            if 'Value' in self.completer.options[words[0].upper()]:       # then print the value
                #ToDo: Print True as 'On'
                if display == True: print (to_user (words[0], None, self.completer.options[words[0].upper()]['Value']))
                return returns.Ok
        
            if not 'Default' in self.completer.options[words[0].upper()]:   # We are a command
                if False:
                    True
                elif words[0] == 'CSTATUS':
                    for s in streamlist:
                        sstate = 'CONNECTED' if ((not self.tnc.streams[s] is None) and (not self.tnc.streams[s]['Connection'] is None)) else 'DISCONNECTED'
                        if sstate == 'CONNECTED':
                            scalls = ('%s>%s' % (self.tnc.streams[s]['Connection'].callFrom, self.tnc.streams[s]['Connection'].callTo))
                            if not self.tnc.streams[s]['Connection'].callDigi == '' and not self.tnc.streams[s]['Connection'].callDigi is None :
                                print (self.tnc.streams[s]['Connection'].callDigi)
                                scalls += "," + ",".join(self.tnc.streams[s]['Connection'].callDigi)
                        else:
                            scalls = 'NO CONNECTION'
                        if display == True: print ('%s stream    State %s\t\t%s' %(s, sstate, scalls))
                    return returns.Ok
                elif words[0] == 'CALIBRA':
                    return returns.NotImplemented
                elif words[0] == 'CALSET':
                    return returns.NotImplemented
                elif words[0] == 'CONVERS':
                    self.tnc.mode = self.tnc.modeConverse
                    return returns.Ok
                elif words[0] == 'DISCONNE':
                    self.tnc.streams['A']['Connection'].disconnect()
                    return returns.Ok
                elif words[0] == 'ID':
                    return returns.NotImplemented
                elif words[0] == 'MHCLEAR':
                    self.tnc.mheard = []
                    return returns.Ok
                elif words[0] == 'MHEARD':
                    for c in self.tnc.mheard:
                        #print (c)
                        #dt.replace(tzinfo=timezone.utc)
                        print ('%s\t\t\t%s' % (c, self.displaydatetime(self.tnc.mheard[c])))
                    return returns.Ok 
                elif words[0] == 'RESTART':
                    return returns.NotImplemented
                elif words[0] == 'TRANS':
                    self.tnc.mode = self.tnc.modeTrans
                    return returns.Ok
                elif words[0] == 'STATUS':
                    return returns.NotImplemented

        if len(words) > 1 and words[0].upper() in self.completer.options:
            # Arbitary length strings
            uc = words[0].upper()
            if 'Default' in self.completer.options[uc]:
                default = self.completer.options[uc]['Default']
                if not 'Value' in self.completer.options[uc]:
                    self.completer.options[uc]['Value'] = default #init
            if 'Minimum' in self.completer.options[uc]:
                if self.completer.options[uc]['Minimum'] == -1:
                    length = len(words[0]) + 1
                    new_words = words # Make a new list
                    new_words.pop(0) # remove the first item
                    new_words = " ".join(new_words)
                    if display == True: print (to_user (uc, self.completer.options[uc]['Value'], new_words))
                    self.completer.options[uc]['Value'] = new_words
                    return returns.Ok
                return returns.Bad


        if len(words) == 2 and words[0].upper() in self.completer.options:
            # Start with two words, and go from there 

            # Start with On/Off
            uc = words[0].upper()
            if 'Default' in self.completer.options[uc]:
                default = self.completer.options[uc]['Default']
                if not 'Value' in self.completer.options[uc]:
                    self.completer.options[uc]['Value'] = default #init
                if not 'Value' in self.completer.options[uc]:
                    self.completer.options[uc]['Value'] = default #init
                if words[1].upper() == 'ON' and 'On' in self.completer.options[uc]['Commands']:
                    if display == True: print( to_user (uc, self.completer.options[uc]['Value'], True))
                    self.completer.options[uc]['Value'] = True
                    return returns.Ok
                if words[1].upper() == 'OFF' and 'Off' in self.completer.options[uc]['Commands']:
                    if display == True: print (to_user (uc, self.completer.options[uc]['Value'], False))
                    self.completer.options[uc]['Value'] = False
                    return returns.Ok
                if len(default) == 3 and default[0] == '$' and len(words[1]) == 3:
                    # We need to enter a HEX value, of the form $NN
                    if words[1][0] == '$' and is_hex(words[1][1:]):
                        if display == True: print (to_user (uc, self.completer.options[uc]['Value'], words[1]))
                        self.completer.options[uc]['Value'] = words[1]
                        return returns.Ok                    

    
        if len(words) == 2:
            uc = words[0].upper()
            # Commands in the form 'TXDELAY 20'
            if words[1].isnumeric():
                number = int (words[1])
                if 'Min' in self.completer.options[uc] and 'Max' in self.completer.options[uc]:
                    if number < self.completer.options[uc]['Min']: 
                        return returns.Bad
                    if number > self.completer.options[uc]['Max']: 
                        return returns.Bad
                    if display == True: print (to_user (uc, self.completer.options[uc]['Value'], number))
                    self.completer.options[uc]['Value'] = number   
                    return returns.Ok

        return returns.Eh

        print ('Err: Did not find %s' %(words))










def _on_receive_trace (frame): 
    bytes = frame.__bytes__() 
    paclen = len(bytes)
    output (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
    offset = 0
    #6, 42, 59

    while offset < paclen:
        # deal with the string as a list
        line = list(('%03x                                                                        ' % (offset)))
        i = 0
        hpos = 6
        sapos = 42
        apos = 59
        hexcount = 0 
        while (offset + i < paclen) and (i < 16):
            ascii = bytes[offset+i]
            hex = "{:02x}".format(ascii)
            line [hpos] = hex[0]
            line [hpos+1] = hex [1]
            hpos += 2
            hexcount += 1

            if hexcount == 4 or hexcount == 8 or hexcount == 12:
                hpos += 1

            if chr(bytes[offset+i] >> 1).isprintable():
                line [sapos] = chr(bytes[offset+i] >> 1)
            else:
                line[sapos] = '.'
            sapos += 1

            if chr(bytes[offset+i]).isprintable():
                line [apos] = chr(bytes[offset+i])
            else:
                line[apos] = '.'
            apos += 1
            i += 1
        offset += 0x10

        line = "".join(line)
        output (line)



def _on_receive_monitor (frame, completer, tnc):

    calls = re.split (r"[*>,]", str(frame.header))
    calls = [value for value in calls if value != '']
    lcalls = completer.options['LCALLS']['Value'].split(',')
    budlist = completer.options['BUDLIST']['Value']
    mall = completer.options['MALL']['Value']
    mcon = completer.options['MCON']['Value']
    mrpt = completer.options['MRPT']['Value']
    headerln = completer.options['HEADERLN']['Value']
    adrdisp = completer.options['ADRDISP']['Value']
    trace = completer.options['TRACE']['Value']
    mtrans = completer.options['MTRANS']['Value']


    if tnc.mode == tnc.modeTransparent:
        if mtrans == False:
            # No Monitoring
            return False

    displayPacket = False

    if tnc.connected:
        if mcon == False:
            # do not display in Connected mode if mcon = False
            return

    #print (calls)
    #print (lcalls)
    #print (budlist)
    if set(calls).intersection(lcalls):
        if budlist == True:
            # Monitor these
            True
        else:
            # Ignore these
            return
    else:
        if budlist == True:
            # Ignore these
            return
        else:
            # Monitor these
            True

    if mall:
        # mon connected and unconnected
        True
    else:
        # mon unconnected only
        if type(frame) is aioax25.frame.AX25UnnumberedInformationFrame:
            True
        else:
            return

    if completer.options['MONITOR']['Value']: # MONITOR ON
        True
    else:
        # If Monitor is OFF, Return
        return
        
    #MRPT On: WB9FLW>AD7I,K9NG*,N2WX-7:Hi Paul.
    #MRPT OFF: WB9FLW>AD7I:Hi Paul.
    if mrpt:
        callsigns = frame.header.source.__str__() + '>' + frame.header.destination.__str__() + ',' + frame.header.repeaters.__str__()
    else:
        callsigns = frame.header.source.__str__() + '>' + frame.header.destination.__str__()


    c = frame.control
    # x1 = RR; x5 = RNR, x9 = REJ, 03 = UI, 0F = DM, 2F = SABM, 43 = DISC, 63 = UA, 87 = FRMR, even = I
    if False:
        True
    elif (c & 0x0F) == 0x01:
        control = 'RR'
    elif (c & 0x0F) == 0x05:
        control = 'RNR'
    elif (c & 0x0F) == 0x09:
        control = 'REJ'
    elif c == 0x03:
        control = 'UI'
    elif c == 0x0F:
        control = 'DM'
    elif c == 0x2F:
        control = 'SABM'
    elif c == 0x43:
        control = 'DISC'
    elif c == 0x63:
        control = 'UA'
    elif c == 0x87:
        control = 'FRMR'
    elif (c & 0x01) == 0x00:
        control = 'I'

    #ToDo: Check Polarity
    if frame.header.cr:
        control = control + ' C'
    else:
        control = control + ' R'

    #ToDo: Check Polarity
    if frame.pf:
        control = control + ' P'
    else:
        control = control + ' F'

    if (c & 0x01) == 0x00:
        # Sequenced I frames
        control = control + ' ToDo-Sn'

    if  ((c & 0x01) == 0x00) or ((c & 0x0F) == 0x01) or ((c & 0x0F) == 0x05) or ((c & 0x0F) == 0x09):
        # I, REJ, RNR, RR
        control = control + ' ToDo-Rn'

    control = ' <' + control + '>:'
    

    #ADRdisp - default ON - N4UQQ>N4UQR,TPA5* <UI R>:This is a monitored frame.
    if headerln:
        #HEADERLN On: KV7D>N2WX: Go ahead and transfer the file.
        if adrdisp:
            output (callsigns + control)
        output (frame.payload)
    else:
        #HEADERLN Off: N2WX>KV7D:
        #           Sorry, I'm not quite ready yet.
        if adrdisp:
            output (callsigns + control + str(frame.payload.decode()))
        else:
            output (frame.payload)

    if trace:
        # Trace mode enabled.
        _on_receive_trace (frame)




def output(line):
    # So I can abstract print
    print (line)
