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
    'list': ['files', 'directories'],
    'print': ['byname', 'bysize'],
    'stop': [],
    '8bitconv': ['on', 'off'],          # Strip high-order bit when in convers mode
    'AUtolf': ['on', 'off'],            # Send Linefeed to terminal after each CR
    'AWlen': [7, 8],                    # Terminal character length (7/8)
    'Ax2512v2': ['on', 'off'],          # Run as version 1.0 of AX.25
    'AXDelay': [],                      # (O-180 * 0.1 set) Voice Repeater keyup delay
    'AXHang': [],                       # (O-20 * 0.1 set) Voice Repeater hang time
    'Beacon': ['every', 'after'],       # Every/After O-250 *lO sec
    'BKondel': ['on', 'off'],           # Send BS SP BS for each DELETE character
    'BText': [],                        # (120 char) Text to be sent for a beacon)
    'BUdlist': ['on', 'off'],           # Stations in Lcalls are ignored
    'CALibra': [],                      # Used to calibrate the builtin modem
    'CALSet' : [],                      # Used with CALibrate
    'CANline': [],                      # (Control-X) The Line Delete character
    'CANPac': [],                       # (Ctrl-Y) Cancel current character
    'CHech': [],                        # O-250 * 10 set) Idle link time out
    'CLKADJ': [],                       # (O-65535) Real time clock adjustment constant
    'CMDtime': [],                      # (O-255 set) transparent mode escape timer
    'CMSG': ['on', 'off'],              # Don't send CTEXT when user links to your TNC
    'COMmand': [],                      # Char to escape from CONVERS mode to command mode
    'CONMode': ['convers', 'trans'],    # Mode to enter when link established
    'Connect': [],                      # Establish Link with station via optional stations
    'CONOk': ['on', 'off'],             # Allow stations to establish a link with your TNC
    'CONPerm': ['on', 'off'],           # If ON always keep this link up (never Disconnect)
    'CONStamp': ['on', 'off'],          # If ON print date & time stamp on connect messages
    'CStatus':  [],                     # Prints the status of all links (Str%eams)
    'CONVers': [],                      # Enter Converse mode from command mode
    'CPactime': ['on', 'off'],          # Don? forward data based on timers (see Pactime)
    'CR': ['on', 'off'],                # Append a Carriage Return to each data packet
    'CText': [],                        # (120 Ch) Connect Message Text (see CMSG)
    'DAytime': [],                      # Date and time for real time clock
    'DAYUsa': ['on', 'off'],            # Print date as mm/dd/yy instead of dd-mm-yy
    'DELete': ['on', 'off'],            # The character delete is BS ($08) not DEL ($7E')
    'DIGipeat': ['on', 'off'],          # Allow stations to use you as a Digipeater
    'Disconne': [],                     # Request a link disconnect from the other station
    'Display': ['Async',                # (Async/Character/Id/Monitor/Timing) Parameters
                'Character', 
                'Id', 
                'Monitor',
                'Timing'],
    'DWait': [],                        # (O-250 * 10 msec) Delay to let digipeater repeat
    'Echo': ['on', 'off'],              # Echo characters typed on keyboard to terminal
    'Escape': ['on', 'off'],            # Don't translate ES@ character ($lB) to $ ($24:)
    'Flow': ['on', 'off'],              # Don't print to terminal while user is typing
    'FRack': [],                        # (l-15 set) Time needed to ack a packet per station
    'FUlldup': ['on', 'off'],           # Operate in Simplex mode
    'HEaderln': ['on', 'off'],          # Print the frame header and text on the same line
    'HID': ['on', 'off'],               # Don't send an ID packet every 9.5 mins when active
    'ID': [],                           # Force an ID packet (UI frame Via UNproto path)
    'LCALLS': [],                       # (O-8 calls) to receive or ignore stations (BUDLIST)
    'LCok': ['on', 'off'],              # Do not convert lower case to UPPER CASE on terminal
    'LCSTREAM': ['on', 'off'],          # Convert the stream select specifer to Upper case
    'LFadd': ['on', 'off'],             # Add a Line Feed after each CR send to the terminal
    'MA11': ['on', 'off'],              # Monitor data frames as well as beacons
    'MAXframe': [],                     # The window size for outstanding frames
    'MCOM': ['on', 'off'],              # Monitor only data frames instead of all types
    'MCon': ['on', 'off'],              # Don't monitor frames when linked to another station
    'MFilter': [],                      # Up to 4 characters to be removed from monitored data
    'MHClear': [],                      # Clear the calls Heard list
    'MHeard': [],                       # Display the calls heard and date/time if clock set
    'Monitor': ['on', 'off'],           # Monitor mode on - see BUDLIST, MALL, MCON, MSTAMP
    'MRpt': ['on', 'off'],              # Display the digipeater path in monitored frames
    'MStamp': ['on', 'off'],            # Monitored frames are Not time stamped
    'MYAlias': [],                      # An identifier for a digipeater
    'MYcall': [],                       # The station callsign for ID and linking
    'NEwmode': ['on', 'off'],           # The TNC acts like a TNC I for changing modes
    'NOmode': ['on', 'off'],            # If ON allow explicit mode change only
    'NUcr': ['on', 'off'],              # Don't send NULLS ($00) after a CR
    'NULf': ['on', 'off'],              # Don't send Nulls after a LF
    'NULLS': [],                        # (O-30) Number of nulls to send as requested
    'Paclen': [],                       # (O-255,0=256) size of the data field in a data frame
    'PACTime': ['Every', 'After'],      # (Every/After O-250 *lOO ms) Data forwarding timer
    'PARity': [0,1,2,3],                # (O-3) Terminal parity 0,2=None l=odd 3=even
    'PASs': [],                         # (CTRL-V) char to allow any character to be typed
    'PASSAll': ['on', 'off'],           # Accept only frames with valid CRCs
    'RECOnnect': [],                    # Like Connect but to restablish a link via a new path
    'REDisplay': [],                     # (CTRL-R) char to print the current input buffer
    'RESET': [],                        # RESET bbRAM PARAMETERS TO DEFAULTS
    'RESptime': [],                     # (O-250 * 100 ms) minimum delay for sending an ACK
    'RESTART': [],                      # Perform a power on reset
    'RETry': [],                        # (O-15) maximum number of retries for a frame
    'Screenln': [],                     # (O-255) Terminal output width
    'SEndpac': [],                      # (CR) Char to force a frame to be sent)
    'STArt': [],                        # (CTRL-Q) the XON for data TO the terminal
    'STOp': [],                         # (CTRL-S) the XOFF for data TO the terminal
    'STREAMCa': ['on', 'off'],          # Don't show the callsign after stream id
    'STREAMDbl': ['on', 'off'],         # Don't print the stream switch char twice (!!A)
    'STReamsw': [],                     # Character to use to change streams (links)
    'TRAce': ['on', 'off'],             # Hexidecimal trace mode is disabled
    'TRANS': [],                        # The TNC enters Transparent data mode
    'TRFlow': ['on', 'off'],            # Disable flow control to the Terminal (Trans mode)
    'TRIes': [],                        # (O-15) set or display the current retry counter
    'TXdelay': [],                      # (O-120 * 10ms) Keyup delay for the transmitter
    'TXFlow': ['on', 'off'],            # Disable flow control to the TNC (Transparent mode)
    'Unproto': [],                      # Path and address to send beacon data
    'Users': [],                        # Sets the number of streams (links) allowed
    'Xflow': ['on', 'off'],             # XON/XOFF Flow control enabled instead of hardware
    'XMitok': ['on', 'off'],            # Allow transmitter to come on
    'XOff': [],                         # (CTRL-S) Character to stop data from terminal
    'XON': [],                          # (CTRL-Q) Character to start data from terminal




})


readline.set_completer(completer.complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')

# Prompt the user for text
input_loop()

