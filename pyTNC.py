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
        self.options['HELP'] = {}
        self.options['HELP']['Commands'] = list(self.options)

        self.options['HELP']['HELP'] = 'Get help on commands'
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
                        #print (candidates)
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

def input_process (line):

    words = line.upper().split()
    print (words)
    if len(words) == 0:
        return returns.Ok

    if False:
        True
    elif words[0] == 'HELP':
        if len(words) == 1:
            print (completer.options['Help']['Help'])
            return returns.Ok
        if len(words) >= 2:
            if words[1] in completer.options:
                uc = words[1].upper()
                if 'Help' in completer.options[uc]:
                    print (completer.options[uc]['Help'])
                    return returns.Ok
                else:
                    print ('No help available')
                    return returns.Ok
        return returns.Bad
    elif words[0] == 'DUMP':
        if len(words) == 0:
            for o in completer.options:
                if 'Value' in completer.options[o]:
                    #ToDo: Print True as On
                    print (('%s = %s') % ( o, completer.options[o]['Value']))
            return returns.Ok
        for o in completer.options:
            if o == words[1] and 'Value' in completer.options[o]:
                #ToDo: Print True as On
                print (('%s = %s') % ( o, completer.options[o]['Value']))
            return returns.Ok
        return returns.Bad        
    

    if len(words) == 1 and words[0].upper() in completer.options:        # If a single word only, and it has a value,
        if 'Value' in completer.options[words[0].upper()]:       # then print the value
            #ToDo: Print True as 'On'
            print (('%s = %s') % ( words[0], completer.options[words[0].upper()]['Value']))
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

    if len(words) > 1 and words[0].upper() in completer.options:
        # Arbitary length strings
        uc = words[0].upper()
        if 'Minimum' in completer.options[uc]:
            if completer.options[uc]['Minimum'] == -1:
                length = len(words[0]) + 1
                new_words = words # Make a new list
                new_words.pop(0) # remove the first item
                new_words = " ".join(new_words)
                completer.options[uc]['Value'] = new_words
                return returns.Ok
            return returns.Bad


    if len(words) == 2 and words[0].upper() in completer.options:
        # Start with two words, and go from there 

        # Start with On/Off
        uc = words[0].upper()
        if 'Default' in completer.options[uc]:
            default = completer.options[uc]['Default']
            if words[1].upper() == 'ON' and 'On' in completer.options[uc]['Commands']:
                completer.options[uc]['Value'] = True
                return returns.Ok
            if words[1].upper() == 'OFF' and 'Off' in completer.options[uc]['Commands']:
                completer.options[uc]['Value'] = False
                return returns.Ok
            if len(default) == 3 and default[0] == '$' and len(words[1]) == 3:
                # We need to enter a HEX value, of the form $NN
                if words[1][0] == '$' and is_hex(words[1][1:]):
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
                completer.options[uc]['Value'] = number   
                return returns.Ok

    return returns.Eh

    print ('Err: Did not find %s' %(words))



def input_loop():
    line = ''
    while line != 'stop':
        #line = input('Prompt ("stop" to quit): ')
        line = input('cmd: ')
        print('Dispatch {}'.format(line))
        r = input_process(line)
        if r == returns.Eh:
            print ('?EH')
        elif r == returns.Bad:
            print ('?BAD')



TNC2_ROM = {
    'list': {'Commands': ['files', 'directories']},
    'print': {'Commands': ['byname', 'bysize']}, 
    'stop': {'Commands': []}, 
    'Dump': {'Commands': [], 'Help': 'Dump all values'}, # VK2TDS custom command
    '8bitconv': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Strip high-order bit when in convers mode'},
    'AUtolf': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Send Linefeed to terminal after each CR'},
    'AWlen': {'Commands': [7, 8],  'Default': '7', 'Min': 7, 'Max': 8, 'Help': 'Terminal character length (7/8)'},
    'Ax2512v2': {'Commands': ['On', 'Off'],  'Default': 'Off', 'Help': 'Run as version 1.0 of AX.25'},
    'AXDelay': {'Commands': [], 'Default': '0', 'Min': 0, 'Max': 180, 'Help': '(O-180 * 0.1 set) Voice Repeater keyup delay'},
    'AXHang': {'Commands': [],  'Default': '0', 'Min': 0, 'Max': 20, 'Help': '(O-20 * 0.1 set) Voice Repeater hang time'},
    'Beacon': {'Commands': ['every', 'after'], 'Minimum': 2, 'Default': 'Every 0', 'Help': 'Every/After O-250 *lO sec'},
    'BKondel': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Send BS SP BS for each DELETE character'},
    'BText': {'Commands': [],  'Default': 'Beacon Text', 'Minimum': -1, 'Help': '(120 char) Text to be sent for a beacon)'},
    'BUdlist': {'Commands': ['On', 'Off'],  'Default': 'Off', 'Help': 'Stations in Lcalls are ignored'},
    'CALibra': {'Commands': [], 'Help': 'Used to calibrate the builtin modem'},
    'CALSet' : {'Commands': [], 'Help': 'Used with CALibrate'},
    'CANline': {'Commands': [], 'Default': '$18', 'Help': '(Control-X) The Line Delete character'},
    'CANPac': {'Commands': [], 'Default': '$19', 'Help': '(Ctrl-Y) Cancel current character'},
    'CHeck': {'Commands': [], 'Default': '30', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 set) Idle link time out'},
    'CLKADJ': {'Commands': [], 'Default': '0', 'Min': 0, 'Max': 65536, 'Help': '(O-65535) Real time clock adjustment constant'},
    'CMDtime': {'Commands': [], 'Default': '1', 'Min': 0, 'Max': 255, 'Help': '(O-255 set) transparent mode escape timer'},
    'CMSG': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t send CTEXT when user links to your TNC'},
    'COMmand': {'Commands': [], 'Default': '$03', 'Help': 'Char to escape from CONVERS mode to command mode'},
    'CONMode': {'Commands': ['convers', 'trans'], 'Default': 'Convers', 'Help': 'Mode to enter when link established'},
    'Connect': {'Commands': [], 'Help': 'Establish Link with station via optional stations'},
    'CONOk': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Allow stations to establish a link with your TNC'},
    'CONPerm': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'If ON always keep this link up (never Disconnect)'},
    'CONStamp': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'If ON print date & time stamp on connect messages'},
    'CStatus':  {'Commands': [], 'Help': 'Prints the status of all links (Streams)'},
    'CONVers': {'Commands': [], 'Help': 'Enter Converse mode from command mode'},
    'CPactime': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t forward data based on timers (see Pactime)'},
    'CR': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Append a Carriage Return to each data packet'},
    'CText': {'Commands': [],  'Default': 'Hello and Good Morning', 'Minimum': -1, 'Help': '(120 Ch) Connect Message Text (see CMSG)'},
    'DAytime': {'Commands': [], 'Help': 'Date and time for real time clock'},
    'DAYUsa': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Print date as mm/dd/yy instead of dd-mm-yy'},
    'DELete': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'The character delete is BS ($08) not DEL ($7E)'},
    'DIGipeat': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Allow stations to use you as a Digipeater'},
    'Disconne': {'Commands': [], 'Help': 'Request a link disconnect from the other station'},
    'Display': {'Commands': ['Async',                # 
                'Character', 
                'Id', 
                'Monitor',
                'Timing'], 'Help': '(Async/Character/Id/Monitor/Timing) Parameters'},
    'DWait': {'Commands': [], 'Default': '16', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 10 msec) Delay to let digipeater repeat'},
    'Echo': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Echo characters typed on keyboard to terminal'},
    'Escape': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t translate ES@ character ($lB) to $ ($24:)'},
    'Flow': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Don\'t print to terminal while user is typing'},
    'FRack': {'Commands': [], 'Default': '3', 'Min': 1, 'Max': 15, 'Help': '(l-15 set) Time needed to ack a packet per station'},
    'FUlldup': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Operate in Simplex mode'},
    'HEaderln': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Print the frame header and text on the same line'},
    'HID': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t send an ID packet every 9.5 mins when active'},
    'ID': {'Commands': [], 'Help': 'Force an ID packet (UI frame Via UNproto path)'},
    'LCALLS': {'Commands': [], 'Default': '', 'Minimum': -1, 'Help': '(O-8 calls) to receive or ignore stations (BUDLIST)'},
    'LCok': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Do not convert lower case to UPPER CASE on terminal'},
    'LCSTREAM': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Convert the stream select specifer to Upper case'},
    'LFadd': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Add a Line Feed after each CR send to the terminal'},
    'MA11': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Monitor data frames as well as beacons'},
    'MAXframe': {'Commands': [], 'Default': '4', 'Min': 1, 'Max': 7, 'Help': 'The window size for outstanding frames'},
    'MCOM': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Monitor only data frames instead of all types'},
    'MCon': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t monitor frames when linked to another station'},
    'MFilter': {'Commands': [], 'Minimum': -1, 'Help': 'Up to 4 characters to be removed from monitored data'},
    'MHClear': {'Commands': [], 'Help': 'Clear the calls Heard list'},
    'MHeard': {'Commands': [], 'Help': 'Display the calls heard and date/time if clock set'},
    'Monitor': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Monitor mode on - see BUDLIST, MALL, MCON, MSTAMP'},
    'MRpt': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Display the digipeater path in monitored frames'},
    'MStamp': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Monitored frames are Not time stamped'},
    'MYAlias': {'Commands': [], 'Minimum': -1, 'Help': 'An identifier for a digipeater'},
    'MYcall': {'Commands': [], 'Default': 'N0CALL', 'Help': 'The station callsign for ID and linking'},
    'NEwmode': {'Commands': ['On', 'Off'],  'Default': 'Off', 'Help': 'The TNC acts like a TNC I for changing modes'},
    'NOmode': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'If ON allow explicit mode change only'},
    'NUcr': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t send NULLS ($00) after a CR'},
    'NULf': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t send Nulls after a LF'},
    'NULLS': {'Commands': [], 'Default': '0', 'Min': 0, 'Max': 30, 'Help': '(O-30) Number of nulls to send as requested'},
    'Paclen': {'Commands': [], 'Default': '128', 'Min': 0, 'Max': 255, 'Help': '(O-255,0=256) size of the data field in a data frame'},
    'PACTime': {'Commands': ['Every', 'After'], 'Minimum': 2, 'Default': 'After 10', 'Help': '(Every/After O-250 *lOO ms) Data forwarding timer'},
    'PARity': {'Commands': [0,1,2,3], 'Default': '3', 'Min': 0, 'Max': 3, 'Help': '(O-3) Terminal parity 0,2=None l=odd 3=even'},
    'PASs': {'Commands': [], 'Default': '$16', 'Help': '(CTRL-V) char to allow any character to be typed'},
    'PASSAll': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Accept only frames with valid CRCs'},
    'RECOnnect': {'Commands': [], 'Help': 'Like Connect but to restablish a link via a new path'},
    'REDisplay': {'Commands': [], 'Default': '$12', 'Help': '(CTRL-R) char to print the current input buffer'},
    'RESET': {'Commands': [], 'Help': 'RESET bbRAM PARAMETERS TO DEFAULTS'},
    'RESptime': {'Commands': [], 'Default': '12', 'Min': 0, 'Max': 250, 'Help': '(O-250 * 100 ms) minimum delay for sending an ACK'},
    'RESTART': {'Commands': [], 'Help': 'Perform a power on reset'},
    'RETry': {'Commands': [], 'Default': '10', 'Min': 0, 'Max': 15, 'Help': '(O-15) maximum number of retries for a frame'},
    'Screenln': {'Commands': [], 'Default': '80', 'Min': 0, 'Max': 255, 'Help': '(O-255) Terminal output width'},
    'SEndpac': {'Commands': [], 'Default': '$0D', 'Help': '(CR) Char to force a frame to be sent)'},
    'STArt': {'Commands': [], 'Default': '$11', 'Help': '(CTRL-Q) the XON for data TO the terminal'},
    'STOp': {'Commands': [], 'Default': '$13', 'Help': '(CTRL-S) the XOFF for data TO the terminal'},
    'STREAMCa': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t show the callsign after stream id'},
    'STREAMDbl': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Don\'t print the stream switch char twice (!!A)'},
    'STReamsw': {'Commands': [], 'Default': '$7c', 'Help': 'Character to use to change streams (links)'},
    'TRAce': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Hexidecimal trace mode is disabled'},
    'TRANS': {'Commands': [], 'Help': 'The TNC enters Transparent data mode'},
    'TRFlow': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Disable flow control to the Terminal (Trans mode)'},
    'TRIes': {'Commands': [], 'Help': '(O-15) set or display the current retry counter'},
    'TXdelay': {'Commands': [], 'Default': '30', 'Min': 0, 'Max': 120, 'Help': '(O-120 * 10ms) Keyup delay for the transmitter'},
    'TXFlow': {'Commands': ['On', 'Off'], 'Default': 'Off', 'Help': 'Disable flow control to the TNC (Transparent mode)'},
    'Unproto': {'Commands': [], 'Default': 'CQ','Minimum': -1, 'Help': 'Path and address to send beacon data'},
    'Users': {'Commands': [], 'Default': '1', 'Min': 1, 'Max': 16, 'Help': 'Sets the number of streams (links) allowed'},
    'Xflow': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'XON/XOFF Flow control enabled instead of hardware'},
    'XMitok': {'Commands': ['On', 'Off'], 'Default': 'On', 'Help': 'Allow transmitter to come on'},
    'XOff': {'Commands': [], 'Default': '$13', 'Help': '(CTRL-S) Character to stop data from terminal'},
    'XON': {'Commands': [], 'Default': '$11', 'Help': '(CTRL-Q) Character to start data from terminal'},
}

TNC2 = {}
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
        input_process (line)

# Prompt the user for text
print ('TAPR TNC2 Clone')
print ('Copyright 2023 Darryl Smith, VK2TDS')
print ('')

input_loop()

