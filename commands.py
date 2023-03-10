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
import re
from datetime import timezone
import datetime
import gnureadline as readline
import aioax25
import library


streamlist = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')



class returns:
    """
    Return values for the command line...
    """

    #returns = SimpleNamespace(**{'Ok':0, 'Eh': 1, 'Bad': 2, 'NotImplemented': 3})
    def __init(self):
        True

    @property
    def Ok(self):
        return 0
    
    @property 
    def Eh(self):
        return 1

    @property
    def Bad(self):
        return 2
    
    @property
    def NotImplemented(self):
        return 3

    

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
        self._Shorter = None
        self._Value = None

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
        if 'Minimum' in ind: 
            self._Minimum = ind['Minimum']
        if 'Shorter' in ind:
            self._Shorter = ind['Shorter']
        if 'Value' in ind:
            self._Value = ind['Value']

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
                        #candidates = self.options.keys()
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        #logging.debug (first)
                        c = self.options[first.upper()].Commands
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
    """
    Interface between user side and radio side. Not 100% sure this will be used in the future. 
    """
    def __init__ (self, callFrom, callTo, callDigi, stream):
        self.callFrom = callFrom
        self.callTo = callTo
        self.callDigi = callDigi
        self.therapist = None
        self.connectedSession = False
        self.stream = stream
        self.stream.Connection = self

        self.output ('Manage a connection from %s to %s via %s' % (callFrom, callTo, callDigi))
        if self.stream.axInit:
            for callback in self.stream.axInit:
                callback (self.stream.Stream)
        if self.stream.cbInit:
            for callback in self.stream.cbInit:
                callback (self.stream.Stream)


    def connect(self):
        self.output ('connection connect')
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
            if self.stream.axConnect:
                for callback in self.stream.axConnect:
                    callback (self.stream.Stream)
            if self.stream.cbConnect:
                for callback in self.stream.cbConnect:
                    callback (self.stream.Stream)
        elif status == False:
            if self.stream.axDisconnect:
                for callback in self.stream.axDisconnect:
                    callback (self.stream.Stream)
            if self.stream.cbDisconnect:
                for callback in self.stream.cbDisconnect:
                    callback (self.stream.Stream)
            self.callFrom = None
            self.callTo = None
            self.callDigi = None

    def axSend(self, text):
        self.output ('axSend %s' % (text))
        if self.stream.axSent:
            for callback in self.stream.axSent:
                callback (text, self.stream.Stream)
        if self.stream.cbSent:
            for callback in self.stream.cbSent:
                callback (text, self.stream.Stream)

    def axReceived (self, text):
        if self.stream.axReceived:
            for callback in self.stream.axReceived:
                callback (text, self.stream.Stream)
        if self.stream.cbReceived:
            for callback in self.stream.cbReceived:
                callback (text, self.stream.Stream)

    def output (self, line):
        print (line)





class process:
    # Process commands
    def __init__ (self, completer, tnc):
        self.completer = completer
        self.tnc = tnc


    def displaydatetime (self, dt):
        if self.completer.options['DAYUSA'].Value:
            if self.completer.options['AMONTH'].Value:
                return dt.strftime ('%d-%b-%Y %H:%M:%S')
            else:
                return dt.strftime ('%m/%d/%Y %H:%M:%S')
        else:
            if self.completer.options['AMONTH'].Value:
                return dt.strftime ('%d-%b-%Y %H:%M:%S')
            else:
                return dt.strftime ('%d/%m/%Y %H:%M:%S')


    def input_cleanup (self, words):
        """
        Cleanup the command line before processing
        """
        # Upper case the first word
        words [0] = words[0].upper()
        if words[0] == 'K':
            words[0] = 'CONNECT'
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
                    for uc in self.completer.options:
                        if not self.completer.options[uc].Help is None:
                            text = '%s\t%s' % (uc, self.completer.options[uc].Help)
                            return (returns.Ok, text)
                    return (returns.Eh, None)
                if words[1] in self.completer.options:
                    uc = words[1].upper()
                    if not self.completer.options[uc].Help is None:
                        text = self.completer.options[uc].Help
                        return (returns.Ok, None)
                    else:
                        text = 'No help available'
                        return (returns.Ok, text)
            return (returns.Bad, None)
        elif words[0] == 'DISPLAY':
            if len(words) == 1: # Display
                cols = 0
                message = ''
                for o in self.completer.options:
                    #if 'Value' in self.completer.options[o].Value:
                                if len(message) > 0:
                                    message = message + '\t\t' + library.to_user (o, None, self.completer.options[o].Value)
                                else:
                                    message = library.to_user (o, None, self.completer.options[o].Value)
                                cols += 1
                                if not self.completer.options['FSCREEN'].Value:
                                        # If we are not in FSCREEN, we only want one column
                                        cols = 4
                                if cols == 4:
                                    message = message + '\n'
                                    cols = 0                        
                return (returns.Ok, message)
            if len(words) > 1: # Display <word>
                group = words[1][0]
                cols = 0
                message = ''
                for o in self.completer.options:
                        if self.completer.options[o].Group == group: 
                            if not self.completer.options[o].Value is None:
                                if len(message) > 0:
                                    message = message + '\t\t' + library.to_user (o, None, self.completer.options[o].Value)
                                else:
                                    message = library.to_user (o, None, self.completer.options[o].Value)
                                cols += 1
                                if 'FSCREEN' in self.completer.options:
                                    if not self.completer.options['FSCREEN'].Value:
                                        # If we are not in FSCREEN, we only want one column
                                        cols = 4
                                if cols == 4:
                                    message = message + '\n'
                                    cols = 0
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
            if len(words) == 1:
                if words[1][0] == '%' or words[1][0] == '&':
                    self.completer.options['CTEXT'].Value = ''
                    return (returns.Ok, 'CTEXT')
        elif words[0] == 'CONNECT':
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
            connection (callFrom, callTo, callDigi, self.tnc.streams['A'])
            self.tnc.streams['A'].Connection.connect()
            return (returns.Ok, None)
        elif words[0] == 'KISSDEV':
            # KISSdev 1 tcp localhost 8001
            if len(words) == 5 and not self.tnc.kiss_interface is None:
                if words[2].upper() == 'TCP':
                    self.tnc.kiss_interface.kissDeviceTCP (int (words[1]), words[3], int (words[4]))
                    return (returns.Ok, " ".join ([words[0], words[1], words[2], words[3]]))
                else: 
                    return (returns.Eh, None)
            else: 
                return (returns.Eh, None)
        elif words[0] == 'KISSPORT':
            # KISSport 1 1
            if len(words) == 3 and not self.tnc.kiss_interface is None:
                self.tnc.kiss_interface.kissPort (int (words[1]), int (words[2]))
                return (returns.Ok, " ".join ([words[0], words[1], words[2]]))
            else:
                return (returns.Eh, None)
        elif words[0] == 'RECONNECT':
            return (returns.NotImplemented, None)


        if len(words) == 1 and words[0].upper() in self.completer.options:        # If a single word only, and it has a value,
            if not self.completer.options[words[0].upper()].Value is None:       # then print the value
                #ToDo: Print True as 'On'
                text = library.to_user (words[0], None, self.completer.options[words[0].upper()].Value)
                return (returns.Ok, text)
        
            if self.completer.options[words[0].upper()].Default is None:   # We are a command
                if False:
                    True
                elif words[0] == 'CSTATUS':
                    text = ""
                    for s in streamlist:
                        sstate = 'CONNECTED' if ((not self.tnc.streams[s] is None) and (not self.tnc.streams[s].Connection is None)) else 'DISCONNECTED'
                        if sstate == 'CONNECTED':
                            scalls = ('%s>%s' % (self.tnc.streams[s].Connection.callFrom, self.tnc.streams[s].Connection.callTo))
                            if not self.tnc.streams[s].Connection.callDigi == '' and not self.tnc.streams[s].Connection.callDigi is None :
                                scalls += "," + ",".join(self.tnc.streams[s].Connection.callDigi)
                        else:
                            scalls = 'NO CONNECTION'
                        if len(text) > 0:
                            text = text + '\n'
                        text = text + '%s stream    State %s\t\t%s' %(s, sstate, scalls)
                    return (returns.Ok, text)
                elif words[0] == 'CALIBRA':
                    return (returns.NotImplemented, None)
                elif words[0] == 'CALSET':
                    return (returns.NotImplemented, None)
                elif words[0] == 'CONVERS':
                    self.tnc.mode = self.tnc.modeConverse
                    return (returns.Ok, None)
                elif words[0] == 'DISCONNE':
                    self.tnc.streams['A'].Connection.disconnect()
                    return (returns.Ok, None)
                elif words[0] == 'ID':
                    return (returns.NotImplemented, None)
                elif words[0] == 'MHCLEAR':
                    self.tnc.mheard = []
                    return (returns.Ok, None)
                elif words[0] == 'MHEARD':
                    text = ""
                    for c in self.tnc.mheard:
                        if len(text) > 0:
                            text = text + '\n'
                        text = text + '%s\t\t\t%s' % (c, self.displaydatetime(self.tnc.mheard[c]))
                    return (returns.Ok, text)
                elif words[0] == 'RESTART':
                    return (returns.NotImplemented, None)
                elif words[0] == 'TRANS':
                    self.tnc.mode = self.tnc.modeTrans
                    return (returns.Ok, None)
                elif words[0] == 'STATUS':
                    return (returns.NotImplemented, None)

        uc = words[0].upper()
        if words[0] in self.completer.options:
            if not self.completer.options[uc].Minimum is None:
                # 'becacon every 5' has a minimum of 2, but len() of 3 
                if len(words) < self.completer.options[uc].Minimum:
                    # too short
                    (returns.Bad, None)
            

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
                        return (returns.Ok, text)
                else:
                    uc = words[0].upper()
                    text = library.to_user (uc, self.completer.options[uc].Value, words[1])
                    self.completer.options[uc].Value = words[1]
                    return (returns.Ok, text)
            
                

        if len(words) > 1 and words[0].upper() in self.completer.options:
            uc = words[0].upper()
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

    def setCompleter (self, c):
        self._completer = c

    def setOutput (self, o):
        self._output = o

    def setTnc (self, t):
        self._tnc = t

    def _on_receive_trace (self, frame): 
        bytes = frame.__bytes__() 
        paclen = len(bytes)
        self.output (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
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
            self.output (line)



    def _on_receive_monitor (self, frame):

        calls = re.split (r"[*>,]", str(frame.header))
        calls = [value for value in calls if value != '']
        lcalls = self._completer.options['LCALLS'].Value.split(',') if not self._completer.options['LCALLS'].Value is None else []
        budlist = self._completer.options['BUDLIST'].Value
        mall = self._completer.options['MALL'].Value
        mcon = self._completer.options['MCON'].Value
        mrpt = self._completer.options['MRPT'].Value
        headerln = self._completer.options['HEADERLN'].Value
        adrdisp = self._completer.options['ADRDISP'].Value
        trace = self._completer.options['TRACE'].Value
        mtrans = self._completer.options['MTRANS'].Value


        if self._tnc.mode == self._tnc.modeTransparent:
            if mtrans == False:
                # No Monitoring
                return False

        displayPacket = False

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
                self.output (callsigns + control)
            self.output (frame.payload)
        else:
            #HEADERLN Off: N2WX>KV7D:
            #           Sorry, I'm not quite ready yet.
            if adrdisp:
                self.output (callsigns + control + str(frame.payload.decode()))
            else:
                self.output (frame.payload)

        if trace:
            # Trace mode enabled.
            self._on_receive_trace (frame)




    def output(self, line):
        self._output (line)
