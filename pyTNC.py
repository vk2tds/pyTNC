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

import commands 

import re
import eliza # for testing



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



class connection:

    def __init__ (self, callFrom, callTo, callDigi):
        self.callFrom = callFrom
        self.callTo = callTo
        self.callDigi = callDigi
        self.therapist = None
        self.connectedSession = False

        self.cbConnected = None
        self.cbDisconnected = None
        self.cbSent = None
        self.cbReceived = None

        print ('Manage a connection from %s to %s via %s' % (callFrom, callTo, callDigi))


    def connect(self):
        if self.callTo == 'ELIZA': 
            self.therapist = eliza.Eliza()
            self.connected = True

    @property
    def connected(self):
        return self.connectedSession
    
    @connected.setter
    def connected(self, status):
        self.connectedSession = status
        if status == True:
            if self.cbConnected:
                self.cbConnected()
        elif status == False:
            if self.cbDisconnected:
                self.cbDisconnected()

    def send(self, text):
        if self.callTo == 'ELIZA':
            reply = self.therapist.respond(text)
            if self.cbSent:
                self.cbSent(text)
            if self.cbReceived:
                self.cbReceived(reply)





def input_cleanup (words):
    global completer
    # Upper case the first word
    words [0] = words[0].upper()
    if words[0] == 'K':
        words[0] = 'CONNECT'
    if not words[0] in completer.options:
        # didnt find the first word, so see if we can do a shorter version
        for o in completer.options:
            if completer.options[o]['Shorter'] == words[0]:
                words[0] = o
    if not words[0] in completer.options:
        #ToDo: Remove one character at a time to see if there is a match            
        True

    if len(words) == 1:
        return words

    # We have more than one word
    if words[0] in completer.options:
        c = completer.options[words[0]]['Commands']
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

    #print (words)
    return words



streams = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None }
def input_process (line, display=True):
    global streams
    
    words = line.split()
    if len(words) == 0:
        return returns.Ok

    words = input_cleanup (words)

    if words[0][0:4] == '/OPT':
        # Oops. We are in Visual Studio Code and tried to run and are already running!
        exit()
        return returns.NotImplemented

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
    elif words[0] == 'LCALLS':
        # special case - blank with %
        if len(words) > 1:
            completer.options['LCALLS']['Value'] = ''
            return returns.Ok
        else:
            if words[1][0] == '%' or words[1][0] == '&':
                completer.options['LCALLS']['Value'] = ''
                return returns.Ok
    elif words[0] == 'CTEXT':
        # special case - blank with %
        if len(words) > 1:
            if words[1][0] == '%' or words[1][0] == '&':
                completer.options['CTEXT']['Value'] = ''
                return returns.Ok
    elif words[0] == 'CONNECT':
        if len(words) < 2:
            return returns.Bad
        # put the words back together and then split them with space and commas
        words = " ".join(words).upper()
        calls = re.split (r"[ ,]", words)
        calls = [value for value in calls if value != '']
        callFrom = completer.options['MYCALL']['Value']
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
        streams['A'] = connection (callFrom, callTo, callDigi)
        streams['A'].cbConnected = tncConnected
        streams['A'].cbDisconnected = tncDisconnected
        streams['A'].cbReceived = tncReceived
        streams['A'].cbSent = tncSend
        streams['A'].connect() # Fake it till you make it
        return returns.Ok
    elif words[0] == 'RECONNECT':
        return returns.NotImplemented

            

    

    if len(words) == 1 and words[0].upper() in completer.options:        # If a single word only, and it has a value,
        if 'Value' in completer.options[words[0].upper()]:       # then print the value
            #ToDo: Print True as 'On'
            if display == True: to_user (words[0], None, completer.options[words[0].upper()]['Value'])
            return returns.Ok
    
        if not 'Default' in completer.options[words[0].upper()]:   # We are a command
            if False:
                True
            elif words[0] == 'CSTATUS':
                for s in ('A', 'B', 'C', 'D', 'E'):
                    sstate = 'CONNECTED' if not streams[s] is None and streams[s].connected else 'DISCONNECTED'
                    if not streams[s] is None:
                        scalls = ('%s>%s' % (streams[s].callFrom, streams[s].callTo))
                        if not streams[s].callDigi == '':
                            scalls += "," + ",".join(streams[s].callDigi)
                    else:
                        scalls = 'NO CONNECTION'
                    if display == True: print ('%s stream    State %s\t\t%s' %(s, sstate, scalls))
                return returns.Ok
            elif words[0] == 'CALIBRA':
                return returns.NotImplemented
            elif words[0] == 'CALSET':
                return returns.NotImplemented
            elif words[0] == 'CSTATUS':
                return returns.NotImplemented
            elif words[0] == 'CONVERS':
                tnc.mode = tnc.modeConverse
                return returns.Ok
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
                tnc.mode = tnc.modeTrans
                return returns.Ok
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










def _on_receive_trace (frame): 
    bytes = frame.__bytes__() 
    paclen = len(bytes)
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
        print (line)




class TNC:


    def __init__(self):
        self.modeConverse = 0
        self.modeTransparent = 1
        self.modeCommand = 2
        self.tncMode = self.modeCommand

        self.tncConnected = False

    @property
    def mode(self):
        return self.tncMode 
    @mode.setter
    def mode (self, m):
        if m == self.modeCommand:
            self.tncMode = m
            readline.parse_and_bind('tab: complete')
        elif m == self.modeTransparent:
            self.tncMode = m
            readline.parse_and_bind('tab: self-insert')
        elif m == self.modeConverse:
            self.tncMode = m
            readline.parse_and_bind('tab: self-insert')

    @property
    def connected (self):
        return self.tncConnected
    
    @connected.setter
    def connected (self, v):
        self.tncConnected = v


tnc = TNC() 



def _on_receive_monitor (frame):
    global tnc

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


    if tnc.mode == tnc.modeTransparent:
        # No Monitoring
        return False

    displayPacket = False

    if tnc.connected:
        if mcon == False:
            # do not display in Connected mode if mcon = False
            return

    print (calls)
    print (lcalls)
    print (budlist)
    if set(calls).intersection(lcalls):
        if budlist == True:
            # Monitor these
            True
        else:
            # Ignore these
            print ('Ignore BUDLIST')
            return
    else:
        if budlist == True:
            # Ignore these
            print ('Ignore BUDLIST')
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
            print (callsigns + control)
        print (frame.payload)
    else:
        #HEADERLN Off: N2WX>KV7D:
        #           Sorry, I'm not quite ready yet.
        if adrdisp:
            print (callsigns + control + str(frame.payload.decode()))
        else:
            print (frame.payload)
    




    #MFILTER Comma separated characters to totally ignore

    #MSTAMP WB9FLW>AD7I,K9NG*,N2WX-71 05/24/97 16:53:19]:Hi Paul.
    #UTC - display in UTC. Default OFF

    #MTRANS Monitoring enabled in TRANS mode *****

    #MONITOR - 1 = No characters > 0x7F; 2 = MONITOR ON

    #ADRdisp - default ON - N4UQQ>N4UQR,TPA5* <UI R>:This is a monitored frame.

    #AMONTH - Default On - All months = three letter alpha

    #CONRPT - if on, LTEXT -> L3TEXT, STEXT, CTEXT (if CMSG = On) sent on connection
    #    break if CMSGDISC????

    #CONStamp - Connection messages are time stamped
    #    *** CONNECTED to KL7EV 105128/97 16:28:31J

    # K === Converse

    #CPOLL?

    #CSTATUS - Status of connection streams

    #CTEXT

    #DGPscall

    #Digipeat - Complex

    #EBEACON - Default OFF - BTEXT echoed to terminal on transmission

    #ENCRYPT, ENSHIFT

    #FSCreen - Display command generates 4 columns - default ON

    #Group - default Off - group monitoring (MASTERM) - Ignore this command

    #STATUS

    if trace:
        # Trace mode enabled.
        _on_receive_trace (frame)















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
    print ('Control %x' %(frame.control))
    print (frame.pid)
    print (frame.frame_payload)
    print (frame)
    print (str(type(frame)))
    print (type(frame) is aioax25.frame.AX25UnnumberedInformationFrame)
    #https://stackoverflow.com/questions/70181515/how-to-have-a-comfortable-e-g-gnu-readline-style-input-line-in-an-asyncio-tas


    _on_receive_monitor(frame)













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










TNC2 = {}
def init():
    global completer

    print ('TAPR TNC2 Clone')
    print ('Copyright 2023 Darryl Smith, VK2TDS')
    print ('')

    for index in commands.TNC2_ROM:
        TNC2[index.upper()] = commands.TNC2_ROM[index]
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
        # Only the upper case letters are an alternative
        completer.options[o]['Shorter'] = ''.join(filter(str.isupper, completer.options[o]['Display']))

    # Custom startup for debugging...
    for custom in ('TRACE ON', 'DAYUSA OFF'):
        input_process (custom, display=True)

    start_ax25()

init()
#input_loop()

streaming_queue = asyncio.Queue()


def tncReceived(text):
    print ('R> %s' % (text))

def tncConnected():
    print ('Connected')
    tnc.mode = tnc.modeConverse # Automatically go into CONVERSE mode


def tncDisconnected():
    print ('Disconnected')

def tncSend(text):
    True
    #print ('Sent')


async def main_async():
    while True:
        chunk = await streaming_queue.get()
        if tnc.mode == tnc.modeCommand:
            
            r = input_process(chunk)
            if r == returns.Eh:
                print ('?EH')
            elif r == returns.Bad:
                print ('?BAD')
            elif r == returns.NotImplemented:
                print ('?Not Implemented')
        elif tnc.mode == tnc.modeConverse:
            streams['A'].send(chunk)
            True
        elif tnc.mode == tnc.modeTrans:
            True


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
                # GNU readline overloads input() 

                if tnc.mode == tnc.modeCommand:
                    chunk = input('cmd: ')
                elif tnc.mode == tnc.modeConverse:
                    chunk = input('> ')
                elif tnc.mode == tnc.modeTrans:
                    chunk = input('> ')

                loop.call_soon_threadsafe(send_chunk, chunk)


                
                
                #print('Dispatch {}'.format(line))
    #except KeyboardInterrupt:
    #    print("cancelling all tasks")
    #    loop.call_soon_threadsafe(cancel_all)
    #    print("joining thread")
    #    event_thread.join()
    #    print("done")