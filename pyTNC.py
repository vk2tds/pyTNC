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






#try:
import gnureadline as readline
#except ImportError:
#    import readline
import logging
import string
from types import SimpleNamespace
import asyncio
from aioax25.kiss import make_device
import aioax25

from aioax25.signal import Signal
from aioax25.interface import AX25Interface
from aioax25.frame import AX25UnnumberedInformationFrame
from threading import Thread



LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format='%(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)

def is_hex(s):
     hex_digits = set(string.hexdigits)
     # if s is long, then it is faster to check against a set
     return all(c in hex_digits for c in s)

class BufferAwareCompleter:

    def __init__(self, options):
        self.options = options
        #self.UC = {}
        #for o in self.options:
        #    self.UC[o.upper()] = o 
        #self.options['HELP'] = {}
        #self.options['HELP']['Commands'] = list(self.options)

        #self.options['HELP']['Help'] = 'Get help on commands'
        #self.UC['HELP'] = 'Help'

        self.current_candidates = []



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

            logging.debug('origline=%s', repr(origline))
            logging.debug('begin=%s', begin)
            logging.debug('end=%s', end)
            logging.debug('being_completed=%s', being_completed)
            logging.debug('words=%s', words)

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

                    logging.debug('candidates=%s',
                                  self.current_candidates)

                except (KeyError, IndexError) as err:
                    logging.error('completion error: %s', err)
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s',
                      repr(text), state, response)
        return response


returns = SimpleNamespace(**{'Ok':0, 'Eh': 1, 'Bad': 2, 'NotImplemented': 3})

def to_user (command, old, new):
    if old is None:
        if new is True:
            new = 'On'
        if new is False:
            new = 'Off'
        print ('%s\t%s' % (command, new))
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
        print ('%s was %s' % (command, old))




def input_process (line, display=True):
    words = line.upper().split()
    if len(words) == 0:
        return returns.Ok

    if words[0][0:4] == '/OPT':
        # Oops. We are in Visual Studio Code and tried to run and are already running!
        exit()

    if False:
        True
    elif words[0] == 'HELP':
        if len(words) == 1:
            if display == True: print (completer.options['HELP']['Help'])
            return returns.Ok
        if len(words) >= 2:
            if words[1].upper() == 'ALL':
                for uc in completer.options:
                    if 'Help' in completer.options[uc]:
                        if display == True: print ('%s\t%s' % (uc, completer.options[uc]['Help']))
                return returns.Ok
            if words[1] in completer.options:
                uc = words[1].upper()
                if 'Help' in completer.options[uc]:
                    if display == True: print (completer.options[uc]['Help'])
                    return returns.Ok
                else:
                    if display == True: print ('No help available')
                    return returns.Ok
        return returns.Bad
    elif words[0] == 'DISPLAY':
        if len(words) == 1:
            for o in completer.options:
                if 'Value' in completer.options[o]:
                    #ToDo: Print True as On
                    if display == True: to_user (o, None, completer.options[o]['Value'])
                    # print (('%s = %s') % ( o, ))
            return returns.Ok
        if len(words) > 1:
            group = words[1][0]
            for o in completer.options:
                if 'Group' in completer.options[o]:
                    if completer.options[o]['Group'] == group: 
                        if 'Value' in completer.options[o]:
                            #ToDo: Print True as On
                            if display == True: to_user (o, None, completer.options[o]['Value'])
            return returns.Ok
        return returns.Bad        
    

    if len(words) == 1 and words[0].upper() in completer.options:        # If a single word only, and it has a value,
        if 'Value' in completer.options[words[0].upper()]:       # then print the value
            #ToDo: Print True as 'On'
            if display == True: to_user (words[0], None, completer.options[words[0].upper()]['Value'])
            return returns.Ok
    
        if not 'Default' in completer.options[words[0].upper()]:   # We are a command
            if False:
                True
            elif words[0] == 'CALIBRA':
                return returns.NotImplemented
            elif words[0] == 'CALSET':
                return returns.NotImplemented
            elif words[0] == 'CSTATUS':
                return returns.NotImplemented
            elif words[0] == 'CONVERS':
                return returns.NotImplemented
            elif words[0] == 'DISCONNE':
                return returns.NotImplemented
            elif words[0] == 'ID':
                return returns.NotImplemented
            elif words[0] == 'MHCLEAR':
                return returns.NotImplemented
            elif words[0] == 'MHEARD':
                return returns.NotImplemented 
            elif words[0] == 'RESTART':
                return returns.NotImplemented
            elif words[0] == 'TRANS':
                return returns.NotImplemented
            elif words[0] == 'STATUS':
                return returns.NotImplemented

    if len(words) > 1 and words[0].upper() in completer.options:
        # Arbitary length strings
        uc = words[0].upper()
        if 'Default' in completer.options[uc]:
            default = completer.options[uc]['Default']
            if not 'Value' in completer.options[uc]:
                completer.options[uc]['Value'] = default #init
        if 'Minimum' in completer.options[uc]:
            if completer.options[uc]['Minimum'] == -1:
                length = len(words[0]) + 1
                new_words = words # Make a new list
                new_words.pop(0) # remove the first item
                new_words = " ".join(new_words)
                if display == True: to_user (uc, completer.options[uc]['Value'], new_words)
                completer.options[uc]['Value'] = new_words
                return returns.Ok
            return returns.Bad


    if len(words) == 2 and words[0].upper() in completer.options:
        # Start with two words, and go from there 

        # Start with On/Off
        uc = words[0].upper()
        if 'Default' in completer.options[uc]:
            default = completer.options[uc]['Default']
            if not 'Value' in completer.options[uc]:
                completer.options[uc]['Value'] = default #init
            if not 'Value' in completer.options[uc]:
                completer.options[uc]['Value'] = default #init
            if words[1].upper() == 'ON' and 'On' in completer.options[uc]['Commands']:
                if display == True: to_user (uc, completer.options[uc]['Value'], True)
                completer.options[uc]['Value'] = True
                return returns.Ok
            if words[1].upper() == 'OFF' and 'Off' in completer.options[uc]['Commands']:
                if display == True: to_user (uc, completer.options[uc]['Value'], False)
                completer.options[uc]['Value'] = False
                return returns.Ok
            if len(default) == 3 and default[0] == '$' and len(words[1]) == 3:
                # We need to enter a HEX value, of the form $NN
                if words[1][0] == '$' and is_hex(words[1][1:]):
                    if display == True: to_user (uc, completer.options[uc]['Value'], words[1])
                    completer.options[uc]['Value'] = words[1]
                    return returns.Ok                    

  
    if len(words) == 2:
        uc = words[0].upper()
        # Commands in the form 'TXDELAY 20'
        if words[1].isnumeric():
            number = int (words[1])
            if 'Min' in completer.options[uc] and 'Max' in completer.options[uc]:
                if number < completer.options[uc]['Min']: 
                    return returns.Bad
                if number > completer.options[uc]['Max']: 
                    return returns.Bad
                if display == True: to_user (uc, completer.options[uc]['Value'], number)
                completer.options[uc]['Value'] = number   
                return returns.Ok

    return returns.Eh

    print ('Err: Did not find %s' %(words))







TNC2_ROM = {
    'list': {'Commands': ['files', 'directories']},
    'print': {'Commands': ['byname', 'bysize']}, 
    'stop': {'Commands': []}, 
    'Help': {'Commands': ['All'], 'Help':'Get help on commands'},
    'DISPLAY': {'Commands': ['ASYNC', 'CHARACTE', 'HEALTH', 'ID', 'LINK', 'MONITOR', 'TIMING'], 'Help': 'Dump all values'}, # VK2TDS custom command
    '8bitconv': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Strip high-order bit when in convers mode'},
    'ANSWRQRA': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Setting ANSWRQRA  to OFF  disables the TNC\'s  ping-response function'},
    'ACKPRIOR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'When ACKPRIOR is  ON, acknowledgments have priority'},
    'AUtolf': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Send Linefeed to terminal after each CR'},
    'AWlen': {'Commands': [7, 8], 'Group': 'A',  'Default': '7', 'Min': 7, 'Max': 8, 'Help': 'Terminal character length (7/8)'},
    'Ax2512v2': {'Commands': ['On', 'Off'], 'Group': 'L',  'Default': 'Off', 'Help': 'Run as version 1.0 of AX.25'},
    'AXDelay': {'Commands': [], 'Group': 'T', 'Default': '0', 'Min': 0, 'Max': 180, 'Help': '(O-180 * 0.1 set) Voice Repeater keyup delay'},
    'AXHang': {'Commands': [], 'Group': 'T',  'Default': '0', 'Min': 0, 'Max': 20, 'Help': '(O-20 * 0.1 set) Voice Repeater hang time'},
    'ACKTIME': {'Commands': [], 'Group': 'T', 'Default': '14', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 mSec) ACKTIME specifies the time required to send an RR or RNR response frame'},
    'Beacon': {'Commands': ['every', 'after'], 'Group': 'I', 'Minimum': 2, 'Default': 'Every 0', 'Help': 'Every/After O-250 *lO sec'},
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
    'CMSG': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Ring a bell on Connect'},
    'COMmand': {'Commands': [], 'Group': 'C', 'Default': '$03', 'Help': 'Char to escape from CONVERS mode to command mode'},
    'CONMode': {'Commands': ['convers', 'trans'], 'Group': 'L', 'Default': 'Convers', 'Help': 'Mode to enter when link established'},
    'Connect': {'Commands': [], 'Help': 'Establish Link with station via optional stations'},
    'CONOk': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Allow stations to establish a link with your TNC'},
    'CONPerm': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'If ON always keep this link up (never Disconnect)'},
    'CONStamp': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'If ON print date & time stamp on connect messages'},
    'CHECKV1': {'Commands': ['On', 'Off'], 'Group': 'T', 'Default': 'Off', 'Help': 'Enables  CHECKtime  (T3)  when running  AX.25  Level  2 Version 1.0 protocol.'},
    'CStatus':  {'Commands': [], 'Help': 'Prints the status of all links (Streams)'},
    'CONVers': {'Commands': [], 'Help': 'Enter Converse mode from command mode'},
    'CMSGDISC': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Automatic disconnect'},
    'CPactime': {'Commands': ['On', 'Off'], 'Group': 'T', 'Default': 'Off', 'Help': 'Don\'t forward data based on timers (see Pactime)'},
    'CR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Append a Carriage Return to each data packet'},
    'CText': {'Commands': [], 'Group': 'I',  'Default': 'Hello and Good Morning', 'Minimum': -1, 'Help': '(120 Ch) Connect Message Text (see CMSG)'},
    'DAytime': {'Commands': [], 'Help': 'Date and time for real time clock'},
    'DAYUsa': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Print date as mm/dd/yy instead of dd-mm-yy'},
    'DELete': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'Off', 'Help': 'The character delete is BS ($08) not DEL ($7E)'},
    'DIGipeat': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'Allow stations to use you as a Digipeater'},
    'Disconne': {'Commands': [], 'Help': 'Request a link disconnect from the other station'},
    'DEADTIME': {'Commands': [], 'Group': 'T', 'Default': '33', 'Min': 0, 'Max': 250, 'Help': '0-250 * 10mSec specifies the  time it  takes a  station\'s receiver  todetect the  fact that  a remote  transmitter  has keyed  up'},
    'Display': {'Commands': ['Async',                # 
                'Character', 
                'Id', 
                'Monitor',
                'Timing'], 'Help': '(Async/Character/Id/Monitor/Timing) Parameters'},
    'DWait': {'Commands': [], 'Group': 'T', 'Default': '16', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 msec) Delay to let digipeater repeat'},
    'Echo': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Echo characters typed on keyboard to terminal'},
    'Escape': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Don\'t translate ES@ character ($lB) to $ ($24:)'},
    'Flow': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Don\'t print to terminal while user is typing'},
    'FIRMRNR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'When this TNC\'s buffers fill, an RNR is sent'},
    'FRack': {'Commands': [], 'Group': 'T', 'Default': '3', 'Min': 1, 'Max': 15, 'Help': '(l-15 set) Time needed to ack a packet per station'},
    'FUlldup': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Operate in Simplex mode'},
    'HEaderln': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Print the frame header and text on the same line'},
    'HID': {'Commands': ['On', 'Off'], 'Group': 'I', 'Default': 'Off', 'Help': 'Don\'t send an ID packet every 9.5 mins when active'},
    'ID': {'Commands': [], 'Help': 'Force an ID packet (UI frame Via UNproto path)'},
    'LCALLS': {'Commands': [], 'Group': 'M', 'Default': '', 'Minimum': -1, 'Help': '(O-8 calls) to receive or ignore stations (BUDLIST)'},
    'LCok': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Do not convert lower case to UPPER CASE on terminal'},
    'LCSTREAM': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'On', 'Help': 'Convert the stream select specifer to Upper case'},
    'LFIGNORE': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'TNC will ignore <LF> characters'},
    'LFadd': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Add a Line Feed after each CR send to the terminal'},
    'MA11': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Monitor data frames as well as beacons'},
    'MAXframe': {'Commands': [], 'Group': 'L', 'Default': '4', 'Min': 1, 'Max': 7, 'Help': 'The window size for outstanding frames'},
    'MCOM': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'Off', 'Help': 'Monitor only data frames instead of all types'},
    'MCon': {'Commands': ['On', 'Off'], 'Group': 'N', 'Default': 'Off', 'Help': 'Don\'t monitor frames when linked to another station'},
    'MNONAX25': {'Commands': ['On', 'Off'], 'Group': 'N', 'Default': 'Off', 'Help': 'Monitors  AX.25  Level   2  Protocol  frames  with   no higher-level protocols (PID = F0)'},
    'MFilter': {'Commands': [], 'Group': 'I', 'Minimum': -1, 'Help': 'Up to 4 characters to be removed from monitored data with commas'},
    'MHClear': {'Commands': [], 'Help': 'Clear the calls Heard list'},
    'MHeard': {'Commands': [], 'Help': 'Display the calls heard and date/time if clock set'},
    'Monitor': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Monitor mode on - see BUDLIST, MALL, MCON, MSTAMP'},
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
    'XOff': {'Commands': [], 'Group': 'C', 'Default': '$13', 'Help': '(CTRL-S) Character to stop data from terminal'},
    'XON': {'Commands': [], 'Group': 'C', 'Default': '$11', 'Help': '(CTRL-Q) Character to start data from terminal'},
}


def _on_receive(interface, frame, match=None):
    # NOTE: Make sure the kissdevice lines up with the one you wnat to listen too

    # interface = ax25int above
    # frame = the incoming UI frame (aioax25.frame.AX25UnnumberedInformationFrame)
    # match = Regular expression Match object, if regular expressions were used in
    #         the bind() call.
    print ('_on_receive')
    print (frame.header)
    print (frame.header.destination)
    print (frame.header.source)
    print (frame.header.repeaters)
    print (frame.header.cr)     # cd = Command Response bit
    print (frame.header.src_cr)
    print (frame.control)
    print (frame.pid)
    print (frame.frame_payload)
    print (frame)
    #https://stackoverflow.com/questions/70181515/how-to-have-a-comfortable-e-g-gnu-readline-style-input-line-in-an-asyncio-tas

    if completer.options['TRACE']['Value']:
        # Trace mode enabled.
        bytes = frame.__bytes__() 
        paclen = len(bytes)
        print (paclen)
        print (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
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
            #print ('Offset %s' % (offset))
            while (offset + i < paclen) and (i < 16):
                #print ('Offset %s %s' % (offset, i))
                ascii = bytes[offset+i]
                hex = "{:02x}".format(ascii)
                line [hpos] = hex[0]
                line [hpos+1] = hex [1]
                hpos += 2
                hexcount += 1

                if hexcount == 4: 
                    hexcount = 5
                elif hexcount == 9:
                    hexcount = 10
                elif hexcount == 14:
                    hexcount = 15

                if chr(bytes[offset+i] >> 1).isprintable():
                    line [sapos] = chr(bytes[offset+i] >> 1)
                else:
                    line[sapos] = '.'
                sapos += 1

                #print ('apos %s' %(apos))
                if chr(bytes[offset+i]).isprintable():
                    line [apos] = chr(bytes[offset+i])
                else:
                    line[apos] = '.'
                apos += 1
                i += 1
            offset += 0x10

            #print (line)
            line = "".join(line)
            print (line)



        print ()





    pass




def start_ax25():
    global logging
    global ax25int

    loop = asyncio.get_event_loop()

    kissdevice = make_device(
    type="tcp", host="localhost", port=8001,
    log=logging.getLogger("ax25.kiss"),
    loop=loop
    )
    kissdevice.open() # happens in background asynchronously


    #That `KISSDevice` class represents all the ports on the KISS interface
    #-- for Direwolf; there can be multiple ports (e.g. on my UDRC-II board,
    #the DIN-6 connector is port 1 and the DB15HD is port 0.).  Most
    #single-port TNCs only implement port 0:

    #kissport = kissdevice[0] # first KISS port on device


    ax25int = aioax25.interface.AX25Interface(
    kissport=kissdevice[0],         # 0 = HF; 2 = USB
    loop=loop, log=logging.getLogger('ax25.interface')
    )

    ax25int.bind (_on_receive, '(.*?)', ssid=None, regex=True)







def input_loop():
        line = ''
        while line != 'stop':
            #line = input('Prompt ("stop" to quit): ')
            line = input('cmd: ')
            #print('Dispatch {}'.format(line))
            r = input_process(line, display=True)
            if r == returns.Eh:
                print ('?EH')
            elif r == returns.Bad:
                print ('?BAD')


TNC2 = {}
def init():
    global completer

    print ('TAPR TNC2 Clone')
    print ('Copyright 2023 Darryl Smith, VK2TDS')
    print ('')

    for index in TNC2_ROM:
        TNC2[index.upper()] = TNC2_ROM[index]
        TNC2[index.upper()]['Display'] = index



    # Register our completer function
    completer = BufferAwareCompleter(TNC2)

    readline.set_completer(completer.complete)

    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')

    # First, process defaults
    for o in completer.options:
        if 'Default' in completer.options[o]:
            line = o + ' ' + completer.options[o]['Default']
            input_process (line, display=False)


    # Custom startup for debugging...
    for custom in ('TRACE ON', ''):
        input_process (custom, display=True)




    # Prompt the user for text


    start_ax25()

init()
#input_loop()

streaming_queue = asyncio.Queue()


async def main_async():
    while True:
        chunk = await streaming_queue.get()
        r = input_process(chunk)
        if r == returns.Eh:
            print ('?EH')
        elif r == returns.Bad:
            print ('?BAD')


        #print("got chunk: ", chunk)


def event_loop(loop):
    #try:
        loop.run_until_complete(main_async())
    #except asyncio.CancelledError:
    #    loop.close()
    #    print("loop closed")


def send_chunk(chunk):
    streaming_queue.put_nowait(chunk)


def cancel_all():
    for task in asyncio.all_tasks():
        task.cancel()




if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    event_thread = Thread(target=event_loop, args=(loop,))
    event_thread.start()
    #try:
#        while True:
#            chunk = input()
#            loop.call_soon_threadsafe(send_chunk, chunk)
    if True: 
            chunk = ''
            while chunk != 'stop':
                #line = input('Prompt ("stop" to quit): ')
                chunk = input('cmd: ')
                loop.call_soon_threadsafe(send_chunk, chunk)
                
                
                #print('Dispatch {}'.format(line))
    #except KeyboardInterrupt:
    #    print("cancelling all tasks")
    #    loop.call_soon_threadsafe(cancel_all)
    #    print("joining thread")
    #    event_thread.join()
    #    print("done")