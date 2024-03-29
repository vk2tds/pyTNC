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

import re
import gnureadline as readline
import aioax25
import library
import enum
from pprint import pprint
import aioax25
import aioax25.peer
import aioax25.kiss

from tabulate import tabulate


streamlist = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')

class returns (enum.Enum):
    Ok = 0
    Eh = 1
    Bad = 2
    NotImplemented = 3


class Individual_Command:
    """
    Class for individual commands for storage of the individual user commands
    """
    def __init__ (self):
        self._Display = None
        self._Commands = []
        self._Group = None
        self._Default = None
        self._Help = None
        self._Min = None
        self._Max = None
        self._Minimum = None
        self._Upper = None
        self._Shorter = None
        self._Implemented = False # Assume not implemented
        self._Notes = None
        self._Value = None
        self._KISS = False
        self._Stage = 1



    def set(self, ind):
        if 'Display' in ind: 
            self._Display = ind['Display']
        if 'Commands' in ind: 
            self._Commands = ind['Commands']
        if 'Group' in ind: 
            self._Group = ind['Group']
        if 'Default' in ind: 
            if len(ind['Default']) > 0:
                self._Default = ind['Default']
        if 'Help' in ind: 
            self._Help = ind['Help']
        if 'Min' in ind: 
            self._Min = ind['Min']
        if 'Max' in ind: 
            self._Max = ind['Max']
        if 'Upper' in ind:
            self._Upper = ind['Upper']
        if 'Minimum' in ind: 
            self._Minimum = ind['Minimum']
        if 'Shorter' in ind:
            self._Shorter = ind['Shorter']
        if 'Value' in ind:
            self._Value = ind['Value']
        if 'Stage' in ind:
            self._Stage = ind['Stage']
        if 'Implemented' in ind:
            self._Implemented = ind['Implemented']
        if 'Notes' in ind:
            self._Notes = ind['Notes']
        if 'KISS' in ind:
            self._KISS = ind['KISS']

    @property
    def Display(self):
        return self._Display
    
    @Display.setter
    def Display(self, disp):
        self._Display = disp

    @property
    def Shorter(self):
        return self._Shorter
    
    @Shorter.setter
    def Shorter(self, short):
        self._Shorter = short

    @property
    def Value(self):
        return self._Value
    
    @Value.setter
    def Value(self, short):
        self._Value = short


    @property
    def Commands(self):
        return self._Commands
    
    @property
    def Group(self):
        return self._Group
    
    @property
    def Default(self):
        return self._Default
    
    @property
    def Help(self):
        return self._Help
    
    @property 
    def Min(self):
        return self._Min
    
    @property
    def Max(self):
        return self._Max
    
    @property
    def Minimum(self):
        return self._Minimum
    
    @property
    def Upper(self):
        return self._Upper
    
    @property
    def Stage(self):
        return self._Stage

    @property
    def KISS(self):
        return self._KISS

    @property
    def Notes(self):
        return self._Notes



class BufferAwareCompleter:
    """
    A class for tab completion, which knows all about the data it is completing
    """
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
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        c = self.options[first.upper()].Commands
                        candidates = [x.upper() for x in c]
                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [
                            w for w in candidates
                            if w.upper().startswith(being_completed.upper())
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




class process:
    # Process commands
    def __init__ (self, completer, tnc, init):
        self.completer = completer
        self.tnc = tnc
        self.init = init

        self.kisscmd = {'TXDELAY': aioax25.kiss.CMD_TXDELAY,
            'PERSIST': aioax25.kiss.CMD_P,
            'SLOTTIME': aioax25.kiss.CMD_SLOTTIME,
            'FULLDUP': aioax25.kiss.CMD_FDUPLEX}


    def input_cleanup (self, words):
        """
        Cleanup the command line before processing
        """
        # Upper case the first word
        words [0] = words[0].upper()
        if words[0] == 'K':
            words[0] = 'CONNECT'
        if words[0] == '?':
            words = ['HELP', 'ALL']

        if not words[0] in self.completer.options:
            # didnt find the first word, so see if we can do a shorter version
            for o in self.completer.options:
                if self.completer.options[o].Shorter == words[0]:
                    words[0] = o
        if not words[0] in self.completer.options:
            # See if there is only ONE unique command possible
            list = []
            for o in self.completer.options:
                if len(o) > len(words[0]):
                    if o[:len(words[0])] == words[0]:
                        # first few characters are the same
                        list.append (o)
            if len(list) == 1:
                words[0] = list[0]

        if len(words) == 1:
            return words

        if not words[0] in self.completer.options: # we didnt find the word at all...
            return words

        if not self.completer.options[words[0]].Upper is None: # Upper case ALL words if needed
            if self.completer.options[words[0]].Upper:
                words = [x.upper() for x in words]

        # We have more than one word
        if words[0] in self.completer.options:
            c = self.completer.options[words[0]].Commands
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
                # TODO: Trim words[0] to the length of the upper case letters 
                for w in c:
                    if words[1].capitalize() == ''.join(filter(str.isupper, str(w))):
                        words[1] = w

        if words[0] == 'CONNECT' or words[0] == 'RECONNECT':
            if len(words) > 3:
                words[2] = words[2].upper()
                if words[2] == 'VIA' or words[2] == 'V':
                    words[2] = 'VIA'

        return words


    def input_process (self, line):
        """
        Process the command line.
        """        

        words = line.split()
        if len(words) == 0:
            return (returns.Ok, None)

        #pre-process the line
        words = self.input_cleanup (words)

        if words[0][0:4] == '/OPT':
            # Oops. We are in Visual Studio Code and tried to run and are already running!
            # TODO make this work
            exit()
            return returns.NotImplemented

        if False:
            pass
        elif words[0] == 'HELP':
            if len(words) == 1:
                text = self.completer.options['HELP'].Help
                return (returns.Ok, text)
            if len(words) >= 2:
                if words[1].upper() == 'ALL':
                    table = []
                    for uc in self.completer.options:
                        if not self.completer.options[uc].Help is None:
                            table.append ([uc, self.completer.options[uc].Help])
                    text = tabulate (table, tablefmt="plain", maxcolwidths=[None, 60])
                    return (returns.Ok, text)
                if words[1].upper() in self.completer.options:
                    uc = words[1].upper()
                    resultList = []
                    if not self.completer.options[uc].Help is None:
                        resultList.append ([uc, self.completer.options[uc].Help])
                        text = tabulate (resultList, tablefmt="plain")
                        return (returns.Ok, text)
                    else:
                        text = 'No help available'
                        return (returns.Ok, text)
            return (returns.Bad, None)
        elif words[0] == 'NOTES':
            table = []
            for uc in self.completer.options:
                if len(words) == 1 or ((len(words) >= 2) and (words[0] == uc)):
                    if not self.completer.options[uc].Notes is None and len(self.completer.options[uc].Notes) > 0:
                        table.append ([uc, self.completer.options[uc].Notes])
            if len(table) > 0:
                text = tabulate (table, maxcolwidths=[None, 50])
                return (returns.Ok, text)
            return (returns.Bad, None)

        elif words[0] == 'DISPLAY':
            narrowList = []
            wideList = []

            if len(words) > 1: # Display <word>
                group = words[1][0]
            for o in self.completer.options:
                display = False
                if len(words) == 1:
                    display = True
                elif len(words) > 1:
                    if self.completer.options[o].Group == group: 
                        display = True
                if display:
                    value = self.completer.options[o].Value
                    if value is True:
                        v = 'On'
                    elif value is False:
                        v = 'Off'
                    elif value is None:
                        v = ''
                    else:
                        v = str(value)
                    if len(v) > 10:
                        wideList.append ([o,v])
                    else:
                        narrowList.append ([o,v])

            message = ''

            workingList = []
            resultList = []
            for entry in narrowList:
                workingList.append (entry[0])
                workingList.append (entry[1])
                if len(workingList) == 8:
                    resultList.append (workingList)
                    workingList = []
            if len(workingList) > 0:
                    resultList.append (workingList)
                    workingList = []

            if len(resultList) > 0:
                message += tabulate (resultList, tablefmt="plain", maxcolwidths=[None, 20,None, 20, None, 20, None, 20])

            if len(wideList) > 1:
                if len(resultList) > 0:
                    message += '\n'
                message += tabulate (wideList, tablefmt="plain", maxcolwidths=[None, 60])
            if len(message) > 0:
                return (returns.Ok, message)
            return (returns.Bad, None)
        elif words[0] == 'LCALLS':
            # special case - blank with % or just LCALLS
            if len(words) == 1:
                self.completer.options['LCALLS'].Value = ''
                return (returns.Ok, 'LCALLS')
            else:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['LCALLS'].Value = ''
                    return (returns.Ok, 'LCALLS')
        elif words[0] == 'CTEXT':
            # special case - blank with %
            if len(words) == 2:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['CTEXT'].Value = ''
                    return (returns.Ok, 'CTEXT')
        elif words[0] == 'IDTEXT':
            # special case - blank with %
            if len(words) == 2:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['IDTEXT'].Value = ''
                    return (returns.Ok, 'IDTEXT')
        elif words[0] == 'ID':
            self.tnc.sendID(self.tnc.activeStream.Port) # Send an ID out the active port on the active stream
            return (returns.Ok, None)
        elif words[0] == 'CONNECT':
            self.tnc.output ('CONNECT is not yet implemented. Remove this message when it does, and update the documentation')
            if len(words) < 2:
                return (returns.Bad, None)
            # put the words back together and then split them with space and commas
            words = " ".join(words).upper()
            calls = re.split (r"[ ,]", words)
            calls = [value for value in calls if value != '']
            callFrom = self.completer.options['MYCALL'].Value
            callTo = calls[1]
            callDigi = []
            if len(calls) > 2:
                if calls[2] == 'VIA':
                    callDigi = calls[3:]
                else:
                    # The third word *MUST* be 'VIA' of there are digipeaters
                    return (returns.Eh, 'Third word must be VIA if used followed by additional calls')
                if len(calls) == 3:
                    # We need digipeaters if there is a 'Via'
                    return (returns.Eh, 'Third word must be VIA if used followed by additional calls')
            #self.tnc.streams['A']['Connection'] = 
            # connection (callFrom, callTo, callDigi, self.tnc, self.tnc.activeStream) # save to stream as well
            # self.tnc.streams['A'].Connection.connect()
            return (returns.NotImplemented, None)
        elif words[0] == 'KISSDEV':
            if len(words) == 1:
                resultList = []
                text = ''
                working = self.completer.options[words[0].upper()].Value.split(',')
                if len(working) > 0:
                    i = 1
                    for w in working:
                        s = w.split(' ')
                        if len(s) >= 3: # Ignore empties
                            resultList.append ([str(i)+':', s[0], s[1], s[2], s[3]])
                            i = i + 1
                text = tabulate (resultList, tablefmt="plain")
                return (returns.Ok, text)
            if len(words) == 2:
                return (returns.NotImplemented, 'TODO: Type KISSDEV 4 to remove the fourth item on the list. ')    






            # KISSdev 1 tcp localhost 8001
            if len(words) == 5 and not self.tnc.kiss_interface is None:
                #TODO: This is append only at the moment
                #TODO Add more than TCP
                if words[2].upper() == 'TCP':
                    self.tnc.kiss_interface.kissDeviceTCP (words[1], words[3], int (words[4]))
                    # TODO: Something better than this next line...
                    line = " ".join ([words[1], words[2], words[3], words[4]])
                    if self.completer.options[words[0].upper()].Value is None or len(self.completer.options[words[0].upper()].Value) == 0:
                        self.completer.options[words[0].upper()].Value = line
                    else:
                        self.completer.options[words[0].upper()].Value += ("," + line)
                    return (returns.Ok, 'KISSDEV add ' + line)
                elif words[2].upper() == 'SERIAL':
                    self.tnc.kiss_interface.kissDeviceSerial (words[1], words[3], int (words[4]))
                    # TODO: Something better than this next line...
                    line = " ".join ([words[1], words[2], words[3], words[4]])
                    if self.completer.options[words[0].upper()].Value is None or len(self.completer.options[words[0].upper()].Value) == 0:
                        self.completer.options[words[0].upper()].Value = line
                    else:
                        self.completer.options[words[0].upper()].Value += ("," + line)
                    return (returns.Ok, 'KISSDEV add ' + line)                    
                else: 
                    return (returns.Eh, None)
            else: 
                return (returns.Eh, None)
        elif words[0] == 'KISSINT':
            if len(words) == 1:
                text = ''
                working = self.completer.options[words[0].upper()].Value.split(',')
                if len(working) > 0:
                    i = 1
                    resultList = []
                    for w in working:
                        s = w.split(' ')
                        if len(s) >= 2: # Ignore empties
                            resultList.append ([str(i) + ':', s[0], s[1]])
                            i = i + 1
                    text = tabulate (resultList, tablefmt="plain")
                return (returns.Ok, text)
            if len(words) == 2:
                return (returns.NotImplemented, 'TODO: Type KISSPORT 4 to remove the fourth item on the list. ')    

            # KISSint 1 1
            if len(words) == 3 and not self.tnc.kiss_interface is None:

                line = " ".join ([words[1], words[2]])
                if self.completer.options[words[0].upper()].Value is None or len(self.completer.options[words[0].upper()].Value) == 0:
                    self.completer.options[words[0].upper()].Value = line
                else:
                    self.completer.options[words[0].upper()].Value += (',' + line)

                if len(self.tnc.kiss_interface.kissInts) == 0:
                    self.tnc.streams[self.tnc.currentStream].Port = (words[1] + ':' + words[2]) # if we dont have a default for this stream, set it

                port = words[1] + ':' + words[2]

                self.tnc.kiss_interface.kissPort (port)

                return (returns.Ok, 'KISSPORT add ' + line)
            else:
                return (returns.Eh, None)
        elif words[0] == 'PORT':
            if len(words) == 1:
                text = ''
                resultList = []
                for ki in self.tnc.kiss_interface.kissInts:
                    (d,i) = ki.split(':')
                    kD = self.tnc.kiss_interface.kissDevices[d]
                    if len(text) > 0:
                        text += '\n'
                    active = ''
                    if self.tnc.streams[self.tnc.currentStream].Port == ki:
                        active = '*'
                    if type(kD) == aioax25.kiss.TCPKISSDevice:
                        resultList.append ([ki +active, str(self.tnc.kiss_interface.kissIntsLastTX[ki] or '<NO_TX_SENT>'), 
                                'TCP', kD._conn_args['host'], 
                                kD._conn_args['port']])
                    if type(kD) == aioax25.kiss.SerialKISSDevice:
                        resultList.append ([ki + active, str(self.tnc.kiss_interface.kissIntsLastTX[ki] or '<NO_TX_SENT>'), 
                                'Serial', kD._conn_args['device'], kD._conn_args['baudrate']])

                    # TODO add other device types.                            
                    text = tabulate (resultList, tablefmt="plain")
                return (returns.Ok, text)
            if len(words) == 2:
                # We are setting the current port
                if words[1] in self.tnc.kiss_interface.kissInts:
                    self.tnc.streams[self.tnc.currentStream].Port = words[1]
                    return (returns.Ok, None)

            return (returns.Eh, None)


        elif words[0] == 'STREAM':
            if len(words) == 1:
                text = 'Stream\t%s' % (self.tnc.currentStream)
                return (returns.Ok, text)
            if len(words) == 2:
                if words[1] in streamlist:
                    self.tnc.currentStream = words[1]
                    self.tnc.receive() # On change stream, check to see if there is any payload to display
            return (returns.Eh, None)

        elif words[0] == 'MYCALL' and len(words) == 2:
            line = str (self.completer.options[words[0].upper()].Value or '')
            self.completer.options[words[0].upper()].Value = words[1].upper()
            self.tnc.kiss_interface.myCallsign (self.completer.options[words[0].upper()].Value)
            return (returns.Ok, 'MYCALL was ' + line)



        elif words[0] == 'RECONNECT':
            return (returns.NotImplemented, None)
        if len(words) == 1 and words[0].upper() in self.completer.options:        # If a single word only, and it has a value,
            if not self.completer.options[words[0].upper()].Value is None:      
                text = library.to_user (words[0], None, self.completer.options[words[0].upper()].Value)
                return (returns.Ok, text)
        
            if self.completer.options[words[0].upper()].Default is None:   # We are a command
                if False:
                    True
                elif words[0] == 'CSTATUS':
                    text = ""
                    resultList = []
                    for s in streamlist:
                        sstate = self.tnc.streams[s].state

                        if sstate == aioax25.peer.AX25Peer.AX25PeerState.CONNECTED:
                            scalls = ('%s>%s' % (self.tnc.streams[s].peer.address, self.tnc.streams[s].peer._station()._address))
                            if not self.tnc.streams[s].peer._repeaters is None and len(self.tnc.streams[s].peer._repeaters) != 0:
                                scalls += ' VIA ' + str (self.tnc.streams[s].peer.reply_path) # TODO improve thsi code
                        else:
                            scalls = 'NO CONNECTION'
                        bytes = 0
                        if not self.tnc.streams[s]._rxBuffer.empty():
                            tempq = self.tnc.streams[s]._rxBuffer.queue
                            for x in tempq:
                                bytes += len(x)
                        resultList.append ([s + ' stream', sstate, scalls, str(bytes)])                        

                    text = tabulate (resultList, tablefmt="plain")
                    return (returns.Ok, text)
                elif words[0] == 'RESET':
                    self.init()
                    return (returns.Ok, None)
                elif words[0] == 'CALSET':
                    return (returns.NotImplemented, None)
                elif words[0] == 'CONVERS':
                    self.tnc.mode = self.tnc.modeConverse
                    self.tnc.receive() # should this be AFTER the OK?
                    return (returns.Ok, None)
                elif words[0] == 'DISCONNE':
                    self.tnc.activeStream.disconnect()
                    return (returns.Ok, None)
                elif words[0] == 'DAYTIME':
                    t = library.displaydatetime (library.datetimenow(self.tnc.completer), self.tnc.completer)
                    return (returns.Ok, t)
                elif words[0] == 'MHCLEAR':
                    self.tnc.mheard = []
                    return (returns.Ok, None)
                elif words[0] == 'MHEARD':
                    text = ""
                    resultList = []
                    for c in self.tnc.mheard:
                        resultList.append ([c, library.displaydatetime(self.tnc.mheard[c], self.completer)])
                    text = tabulate (resultList, tablefmt="plain")
                    return (returns.Ok, text)
                elif words[0] == 'RESTART':
                    return (returns.NotImplemented, None)
                elif words[0] == 'TRANS':
                    self.tnc.mode = self.tnc.modeTrans
                    self.tnc.receive() # should this be after the OK?
                    return (returns.Ok, None)
                elif words[0] == 'STATUS':
                    return (returns.NotImplemented, None)


        uc = words[0].upper()
        if words[0] in self.completer.options:
            if not self.completer.options[uc].Minimum is None:
                # 'becacon every 5' has a minimum of 2, but len() of 3 
                if len(words) < self.completer.options[uc].Minimum:
                    # too short
                    return (returns.Bad, None)
            



        if len(words) == 2 and words[0].upper() in self.completer.options:
            # Start with two words, and go from there 
            # Start with On/Off
            uc = words[0].upper()
            if not self.completer.options[uc] is None:
                default = self.completer.options[uc].Default
                if self.completer.options[uc].Value is None:
                    self.completer.options[uc].Value = default #init
                if words[1].upper() == 'ON' and 'On' in self.completer.options[uc].Commands:
                    text = library.to_user (uc, self.completer.options[uc].Value, True)
                    self.completer.options[uc].Value = True
                    return (returns.Ok, text)
                if words[1].upper() == 'OFF' and 'Off' in self.completer.options[uc].Commands:
                    text = library.to_user (uc, self.completer.options[uc].Value, False)
                    self.completer.options[uc].Value = False
                    return (returns.Ok, text)
                if len(default) == 3 and default[0] == '$' and len(words[1]) == 3:
                    # We need to enter a HEX value, of the form $NN
                    if words[1][0] == '$' and library.is_hex(words[1][1:]):
                        text = library.to_user (uc, self.completer.options[uc].Value, words[1])
                        self.completer.options[uc].Value = words[1]
                        return (returns.Ok, text)

    
         

        if len(words) == 2:
            uc = words[0].upper()
            if words[0] in self.completer.options:
                # Commands in the form 'TXDELAY 20'
                if words[1].isnumeric():
                    number = int (words[1])
                    if not self.completer.options[uc] is None and not self.completer.options[uc].Max is None:
                        if number < self.completer.options[uc].Min: 
                            return returns.Bad
                        if number > self.completer.options[uc].Max: 
                            return returns.Bad
                        text = library.to_user (uc, self.completer.options[uc].Value, number)
                        self.completer.options[uc].Value = number 

                        # # Now process KISS commands
                        # if uc in self.kisscmd.keys():
                        #     # PERPORT
                        #     # we are a KISS comman
                        #     processKISS


                        return (returns.Ok, text)
                else:
                    uc = words[0].upper()
                    text = library.to_user (uc, self.completer.options[uc].Value, words[1])
                    self.completer.options[uc].Value = words[1]
                    return (returns.Ok, text)
            
                

        if len(words) > 1 and words[0].upper() in self.completer.options:
            uc = words[0].upper()

            if words[0] == 'BEACON':
                words[1] = words[1].upper()
                self.completer.options[uc].Value = " ".join (words)
                self.tnc.setBeacon (words[1], words[2])
                return (returns.Ok, self.completer.options[uc].Value)


            #if self.completer.options[uc].Minimum == -1:
            # we know that the length is ok... 
            length = len(words[0]) + 1
            new_words = words # Make a new list
            new_words.pop(0) # remove the first item
            new_words = " ".join(new_words)
            text = library.to_user (uc, self.completer.options[uc].Value, new_words)
            self.completer.options[uc].Value = new_words
            return (returns.Ok, text)

        return (returns.Eh, None)







class Monitor:
    def __init__ (self):
        self._completer = None
        self._output = None
        self._tnc = None

    @property
    def completer (self):
        return self._completer
    
    @completer.setter
    def completer (self, c):
        self._completer = c

    def setOutput (self, o):
        self._output = o

    def setTnc (self, t):
        self._tnc = t

    def _on_receive_trace (self, textInterface, frame): 
        bytes = frame.__bytes__() 
        paclen = len(bytes)
        if self._completer.options['STREAMSHOW'].Value:
            self.output (textInterface + ' ->')
        self.output (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
        offset = 0

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
            self.output (line)



    def _on_receive_monitor (self, interface, frame):


        port = interface._port
        device = 'Unknown'

        if type(port._device) == aioax25.kiss.TCPKISSDevice:
            for d in self._tnc.kiss_interface.kissDevices:
                kD = self._tnc.kiss_interface.kissDevices[d]
                if kD._conn_args['host'] == port._device._conn_args['host'] and kD._conn_args['port'] == port._device._conn_args['port']:
                    device = d

        textInterface = device + ':' + str(port._port)


        calls = re.split (r"[*>,]", str(frame.header))
        calls = [value for value in calls if value != '']
        lcalls = self._completer.options['LCALLS'].Value.split(',') if not self._completer.options['LCALLS'].Value is None else []
        budlist = self._completer.options['BUDLIST'].Value
        mall = self._completer.options['MALL'].Value
        mcon = self._completer.options['MCON'].Value
        mrpt = self._completer.options['MRPT'].Value
        streamshow = self._completer.options['STREAMSHOW'].Value
        headerln = self._completer.options['HEADERLN'].Value
        adrdisp = self._completer.options['ADRDISP'].Value
        trace = self._completer.options['TRACE'].Value
        mtrans = self._completer.options['MTRANS'].Value


        if self._tnc.mode == self._tnc.modeTransparent:
            if mtrans == False:
                # No Monitoring
                return False

        displayPacket = False

        #TODO _tnc.connected is ARGH!!!
        if self._tnc.connected:
            if mcon == False:
                # do not display in Connected mode if mcon = False
                return

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

        if self._completer.options['MONITOR'].Value: # MONITOR ON
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

        #if type(frame) is aioax25.frame.AX25RawFrame:
        #    self.output ('--->AX25RawFrame')
        #    self.output ('RAW' + str(frame))

        if type(frame) is aioax25.frame.AX25RawFrame:
            control = 'RAW PACKET'
        else:
            c = frame.control
            # x1 = RR; x5 = RNR, x9 = REJ, 03 = UI, 0F = DM, 2F = SABM, 43 = DISC, 63 = UA, 87 = FRMR, even = I
            control = '**UNKNOWN %x **' % (c)
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
            elif c == 0x3F:
                control = 'SABM'
            elif c == 0x6F:
                control = 'SABME'
            elif c == 0x7F:
                control = 'SABME'
            elif c == 0x43 or c == 0x53:
                control = 'DISC'
            elif c == 0x63 or c == 0x73:
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
        if hasattr(frame, 'payload'):
            payload = str(frame.payload.decode())
        else:
            payload = '<NO_PAYLOAD>'

        out = ''
        if headerln:
            #HEADERLN On: KV7D>N2WX: Go ahead and transfer the file.
            if adrdisp:
                out = callsigns + control
            else:
                out = payload 
        else:
            #HEADERLN Off: N2WX>KV7D:
            #           Sorry, I'm not quite ready yet.
            if adrdisp:
                out = callsigns + control + payload
            else:
                out = payload

        if streamshow: 
            out = textInterface + ' | ' + out


        self.output (out)

        if trace:
            # Trace mode enabled.
            self._on_receive_trace (textInterface, frame)

    def output(self, line):
        self._output (line)



