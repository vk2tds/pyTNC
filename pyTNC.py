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

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format='%(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)


class BufferAwareCompleter:

    def __init__(self, options):
        self.options = options
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
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [
                            w for w in candidates
                            if w.startswith(being_completed)
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


def input_loop():
    line = ''
    while line != 'stop':
        line = input('Prompt ("stop" to quit): ')
        print('Dispatch {}'.format(line))

# Register our completer function
completer = BufferAwareCompleter({
    'list': {'Commands': ['files', 'directories']},
    'print': {'Commands': ['byname', 'bysize'],
    'stop': {'Commands': [],
    '8bitconv': {'Commands': ['on', 'off'], 'Default': 'Off'         # Strip high-order bit when in convers mode
    'AUtolf': {'Commands': ['on', 'off'], 'Default': 'On'            # Send Linefeed to terminal after each CR
    'AWlen': {'Commands': [7, 8],  'Default': '7'                   # Terminal character length (7/8)
    'Ax2512v2': {'Commands': ['on', 'off'],  'Default': 'Off'          # Run as version 1.0 of AX.25
    'AXDelay': {'Commands': [], 'Default': '0'                      # (O-180 * 0.1 set) Voice Repeater keyup delay
    'AXHang': {'Commands': [],  'Default': '0'                      # (O-20 * 0.1 set) Voice Repeater hang time
    'Beacon': {'Commands': ['every', 'after'],  'Default': 'Every 0'       # Every/After O-250 *lO sec
    'BKondel': {'Commands': ['on', 'off'], 'Default': 'On'           # Send BS SP BS for each DELETE character
    'BText': {'Commands': [],  'Default': 'Beacon Text'                       # (120 char) Text to be sent for a beacon)
    'BUdlist': {'Commands': ['on', 'off'],  'Default': 'Off'           # Stations in Lcalls are ignored
    'CALibra': {'Commands': [],                      # Used to calibrate the builtin modem
    'CALSet' : {'Commands': [],                      # Used with CALibrate
    'CANline': {'Commands': [], 'Default': '$18'                      # (Control-X) The Line Delete character
    'CANPac': {'Commands': [], 'Default': '$19'                       # (Ctrl-Y) Cancel current character
    'CHech': {'Commands': [], 'Default': '30'                        # O-250 * 10 set) Idle link time out
    'CLKADJ': {'Commands': [], 'Default': '0'                      # (O-65535) Real time clock adjustment constant
    'CMDtime': {'Commands': [], 'Default': '1'                      # (O-255 set) transparent mode escape timer
    'CMSG': {'Commands': ['on', 'off'], 'Default': 'Off'              # Don't send CTEXT when user links to your TNC
    'COMmand': {'Commands': [], 'Default': '$03'                      # Char to escape from CONVERS mode to command mode
    'CONMode': {'Commands': ['convers', 'trans'], 'Default': 'Convers'    # Mode to enter when link established
    'Connect': {'Commands': [],                      # Establish Link with station via optional stations
    'CONOk': {'Commands': ['on', 'off'], 'Default': 'On'             # Allow stations to establish a link with your TNC
    'CONPerm': {'Commands': ['on', 'off'], 'Default': 'Off'           # If ON always keep this link up (never Disconnect)
    'CONStamp': {'Commands': ['on', 'off'], 'Default': 'Off'         # If ON print date & time stamp on connect messages
    'CStatus':  {'Commands': [],                     # Prints the status of all links (Str%eams)
    'CONVers': {'Commands': [],                      # Enter Converse mode from command mode
    'CPactime': {'Commands': ['on', 'off'], 'Default': 'Off'         # Don? forward data based on timers (see Pactime)
    'CR': {'Commands': ['on', 'off'], 'Default': 'On'                # Append a Carriage Return to each data packet
    'CText': {'Commands': [],  'Default': 'Hello and Good Morning'                       # (120 Ch) Connect Message Text (see CMSG)
    'DAytime': {'Commands': [],                      # Date and time for real time clock
    'DAYUsa': {'Commands': ['on', 'off'], 'Default': 'Off'            # Print date as mm/dd/yy instead of dd-mm-yy
    'DELete': {'Commands': ['on', 'off'], 'Default': 'Off'            # The character delete is BS ($08) not DEL ($7E')
    'DIGipeat': {'Commands': ['on', 'off'], 'Default': 'On'          # Allow stations to use you as a Digipeater
    'Disconne': {'Commands': [],                     # Request a link disconnect from the other station
    'Display': {'Commands': ['Async',                # (Async/Character/Id/Monitor/Timing) Parameters
                'Character', 
                'Id', 
                'Monitor',
                'Timing'],
    'DWait': {'Commands': [], 'Default': '16'                        # (O-250 * 10 msec) Delay to let digipeater repeat
    'Echo': {'Commands': ['on', 'off'], 'Default': 'On'              # Echo characters typed on keyboard to terminal
    'Escape': {'Commands': ['on', 'off'], 'Default': 'Off'            # Don't translate ES@ character ($lB) to $ ($24:)
    'Flow': {'Commands': ['on', 'off'], 'Default': 'On'              # Don't print to terminal while user is typing
    'FRack': {'Commands': [], 'Default': '3'                        # (l-15 set) Time needed to ack a packet per station
    'FUlldup': {'Commands': ['on', 'off'], 'Default': 'Off'           # Operate in Simplex mode
    'HEaderln': {'Commands': ['on', 'off'], 'Default': 'Off'          # Print the frame header and text on the same line
    'HID': {'Commands': ['on', 'off'], 'Default': 'Off'               # Don't send an ID packet every 9.5 mins when active
    'ID': {'Commands': [],                           # Force an ID packet (UI frame Via UNproto path)
    'LCALLS': {'Commands': [], 'Default': ''                       # (O-8 calls) to receive or ignore stations (BUDLIST)
    'LCok': {'Commands': ['on', 'off'], 'Default': 'On'              # Do not convert lower case to UPPER CASE on terminal
    'LCSTREAM': {'Commands': ['on', 'off'], 'Default': 'On'          # Convert the stream select specifer to Upper case
    'LFadd': {'Commands': ['on', 'off'], 'Default': 'Off'             # Add a Line Feed after each CR send to the terminal
    'MA11': {'Commands': ['on', 'off'], 'Default': 'On'              # Monitor data frames as well as beacons
    'MAXframe': {'Commands': [], 'Default': '4'                     # The window size for outstanding frames
    'MCOM': {'Commands': ['on', 'off'], 'Default': 'Off'              # Monitor only data frames instead of all types
    'MCon': {'Commands': ['on', 'off'], 'Default': 'Off'              # Don't monitor frames when linked to another station
    'MFilter': {'Commands': [],                      # Up to 4 characters to be removed from monitored data
    'MHClear': {'Commands': [],                      # Clear the calls Heard list
    'MHeard': {'Commands': [],                       # Display the calls heard and date/time if clock set
    'Monitor': {'Commands': ['on', 'off'], 'Default': 'On'          # Monitor mode on - see BUDLIST, MALL, MCON, MSTAMP
    'MRpt': {'Commands': ['on', 'off'], 'Default': 'On'              # Display the digipeater path in monitored frames
    'MStamp': {'Commands': ['on', 'off'], 'Default': 'Off'            # Monitored frames are Not time stamped
    'MYAlias': {'Commands': [],                      # An identifier for a digipeater
    'MYcall': {'Commands': [], 'Default': 'N0CALL'                       # The station callsign for ID and linking
    'NEwmode': {'Commands': ['on', 'off'],  'Default': 'Off'          # The TNC acts like a TNC I for changing modes
    'NOmode': {'Commands': ['on', 'off'], 'Default': 'Off'            # If ON allow explicit mode change only
    'NUcr': {'Commands': ['on', 'off'], 'Default': 'Off'              # Don't send NULLS ($00) after a CR
    'NULf': {'Commands': ['on', 'off'], 'Default': 'Off'              # Don't send Nulls after a LF
    'NULLS': {'Commands': [], 'Default': '0'                        # (O-30) Number of nulls to send as requested
    'Paclen': {'Commands': [], 'Default': '128'                       # (O-255,0=256) size of the data field in a data frame
    'PACTime': {'Commands': ['Every', 'After'], 'Default': 'After 10'      # (Every/After O-250 *lOO ms) Data forwarding timer
    'PARity': {'Commands': [0,1,2,3], 'Default': '3'                # (O-3) Terminal parity 0,2=None l=odd 3=even
    'PASs': {'Commands': [], 'Default': '$16'                         # (CTRL-V) char to allow any character to be typed
    'PASSAll': {'Commands': ['on', 'off'], 'Default': 'Off'           # Accept only frames with valid CRCs
    'RECOnnect': {'Commands': [],                    # Like Connect but to restablish a link via a new path
    'REDisplay': {'Commands': [], 'Default': '$12'                     # (CTRL-R) char to print the current input buffer
    'RESET': {'Commands': [],                        # RESET bbRAM PARAMETERS TO DEFAULTS
    'RESptime': {'Commands': [], 'Default': '12'                     # (O-250 * 100 ms) minimum delay for sending an ACK
    'RESTART': {'Commands': [],                      # Perform a power on reset
    'RETry': {'Commands': [], 'Default': '10'                        # (O-15) maximum number of retries for a frame
    'Screenln': {'Commands': [], 'Default': '80'                     # (O-255) Terminal output width
    'SEndpac': {'Commands': [], 'Default': '$0D'                      # (CR) Char to force a frame to be sent)
    'STArt': {'Commands': [], 'Default': '$11'                        # (CTRL-Q) the XON for data TO the terminal
    'STOp': {'Commands': [], 'Default': '$13'                         # (CTRL-S) the XOFF for data TO the terminal
    'STREAMCa': {'Commands': ['on', 'off'], 'Default': 'Off'         # Don't show the callsign after stream id
    'STREAMDbl': {'Commands': ['on', 'off'], 'Default': 'Off'         # Don't print the stream switch char twice (!!A)
    'STReamsw': {'Commands': [], 'Default': '$7c'                     # Character to use to change streams (links)
    'TRAce': {'Commands': ['on', 'off'], 'Default': 'Off'             # Hexidecimal trace mode is disabled
    'TRANS': {'Commands': [],                        # The TNC enters Transparent data mode
    'TRFlow': {'Commands': ['on', 'off'], 'Default': 'Off'            # Disable flow control to the Terminal (Trans mode)
    'TRIes': {'Commands': [],                        # (O-15) set or display the current retry counter
    'TXdelay': {'Commands': [], 'Default': '30'                      # (O-120 * 10ms) Keyup delay for the transmitter
    'TXFlow': {'Commands': ['on', 'off'], 'Default': 'Off'            # Disable flow control to the TNC (Transparent mode)
    'Unproto': {'Commands': [], 'Default': 'CQ'                      # Path and address to send beacon data
    'Users': {'Commands': [], 'Default': '1'                        # Sets the number of streams (links) allowed
    'Xflow': {'Commands': ['on', 'off'], 'Default': 'On'             # XON/XOFF Flow control enabled instead of hardware
    'XMitok': {'Commands': ['on', 'off'], 'Default': 'On'            # Allow transmitter to come on
    'XOff': {'Commands': [], 'Default': '$13'                         # (CTRL-S) Character to stop data from terminal
    'XON': {'Commands': [], 'Default': '$11'                          # (CTRL-Q) Character to start data from terminal




})


readline.set_completer(completer.complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')

# Prompt the user for text
input_loop()

