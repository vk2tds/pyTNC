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




TNC2_ROM = {
    'list': {'Commands': ['files', 'directories']},
    'print': {'Commands': ['byname', 'bysize']}, 
    'stop': {'Commands': []}, 
    'Help': {'Commands': ['All'], 'Help':'Get help on commands'},
    'DISPLAY': {'Commands': ['ASYNC', 'CHARACTE', 'HEALTH', 'ID', 'LINK', 'MONITOR', 'TIMING'], 'Help': 'Dump all values'}, # VK2TDS custom command
    '8bitconv': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'Off', 'Help': 'Strip high-order bit when in convers mode'},
    'ANSWRQRA': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Setting ANSWRQRA  to OFF  disables the TNC\'s  ping-response function'},
    'ACKPRIOR': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'On', 'Help': 'When ACKPRIOR is  ON, acknowledgments have priority'},
    'ADRdisp': {'Commands': ['On', 'Off'], 'Group': 'M', 'Default': 'On', 'Help': 'Address headers on monitored frames will be displayed.'},
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
    'LCALLS': {'Commands': [], 'Group': 'M', 'Default': '%', 'Minimum': -1, 'Help': '(O-8 calls) to receive or ignore stations (BUDLIST)'},
    'LCok': {'Commands': ['On', 'Off'], 'Group': 'A', 'Default': 'On', 'Help': 'Do not convert lower case to UPPER CASE on terminal'},
    'LCSTREAM': {'Commands': ['On', 'Off'], 'Group': 'C', 'Default': 'On', 'Help': 'Convert the stream select specifer to Upper case'},
    'LFIGNORE': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'TNC will ignore <LF> characters'},
    'LFadd': {'Commands': ['On', 'Off'], 'Group': 'L', 'Default': 'Off', 'Help': 'Add a Line Feed after each CR send to the terminal'},
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