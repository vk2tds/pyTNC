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
#import readline
import logging
import string
from types import SimpleNamespace
import asyncio
from aioax25.kiss import make_device
import aioax25
import sys

from aioax25.signal import Signal
from aioax25.interface import AX25Interface
from aioax25.frame import AX25UnnumberedInformationFrame
from threading import Thread
from datetime import datetime
from datetime import timezone

from threading import Semaphore
import eliza
import re


#local
import commands 
import connect 
import ROM



LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format='%(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)


console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
formater = logging.Formatter('%(name)-13s: %(levelname)-8s %(message)s')
console.setFormatter(formater)
logging.getLogger('console').addHandler(console)

loggerscreen = logging.getLogger ('console')



class TNC:


    def __init__(self):
        self.modeConverse = 0
        self.modeTransparent = 1
        self.modeCommand = 2
        self.tncMode = self.modeCommand
        #self.completer = completer

        self.tncConnected = False
        self.mheard = {}
        self.kissinterface = None
        self.exitToCommandMode = '*** COMMAND MODE ***'

        self.monitor = commands.Monitor()

        self.streams = {}
        for s in commands.streamlist:
            self.streams[s] = connect.Stream(s)

    def output (self, line):
        print (line)


    def on_Disconnect (self, cb):
        for s in commands.streamlist:
            self.streams[s].cbDisconnect = cb

    def on_Received (self, cb):
        for s in commands.streamlist:
            self.streams[s].cbReceived = cb
            
    def on_Sent (self, cb):
        for s in commands.streamlist:
            self.streams[s].cbSent = cb
            
    def on_Connect (self, cb):
        for s in commands.streamlist:
            self.streams[s].cbConnect = cb

    def on_Init (self, cb):
        for s in commands.streamlist:
            self.streams[s].cbInit = cb

    def on_axDisconnect (self, cb):
        for s in commands.streamlist:
            self.streams[s].axDisconnect = cb

    def on_axReceived (self, cb):
        for s in commands.streamlist:
            self.streams[s].axReceived = cb
            
    def on_axSent (self, cb):
        for s in commands.streamlist:
            self.streams[s].axSent = cb
            
    def on_axConnect (self, cb):
        for s in commands.streamlist:
            self.streams[s].axConnect = cb

    def on_axInit (self, cb):
        for s in commands.streamlist:
            self.streams[s].axInit = cb



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





    #MFILTER Comma separated characters to totally ignore
    #MSTAMP WB9FLW>AD7I,K9NG*,N2WX-71 05/24/97 16:53:19]:Hi Paul.
    #UTC - display in UTC. Default OFF

    #MONITOR - 1 = No characters > 0x7F; 2 = MONITOR ON

    #AMONTH - Default On - All months = three letter alpha

    #CONRPT - if on, LTEXT -> L3TEXT, STEXT, CTEXT (if CMSG = On) sent on connection
    #    break if CMSGDISC????

    #CPOLL?
    #CSTATUS - Status of connection streams
    #CTEXT
    #DGPscall
    #Digipeat - Complex
    #EBEACON - Default OFF - BTEXT echoed to terminal on transmission
    #ENCRYPT, ENSHIFT
    #Group - default Off - group monitoring (MASTERM) - Ignore this command

    #STATUS






def _on_receive(interface, frame, match=None):
    # NOTE: Make sure the kissdevice lines up with the one you wnat to listen too

    # interface = ax25int above
    # frame = the incoming UI frame (aioax25.frame.AX25UnnumberedInformationFrame)
    # match = Regular expression Match object, if regular expressions were used in
    #         the bind() call.
    #p ('_on_receive')
    #p (frame.header)
    #p (frame.header.destination)
    #p (frame.header.source)
    #p (frame.header.repeaters)
    #p (frame.header.cr)     # cd = Command Response bit
    #p (frame.header.src_cr)
    #p ('Control %x' %(frame.control))
    #p (frame.pid)
    #p (frame.frame_payload)
    #p (frame)
    #p (str(type(frame)))
    #p (type(frame) is aioax25.frame.AX25UnnumberedInformationFrame)
    #https://stackoverflow.com/questions/70181515/how-to-have-a-comfortable-e-g-gnu-readline-style-input-line-in-an-asyncio-tas


    if 'UTC' in completer.options and completer.options['UTC'].Value:
        tnc.mheard[str(frame.header.source)] = datetime.utcnow()
    else:
        tnc.mheard[str(frame.header.source)] = datetime.now()

    #tnc.mheard['VK2TDS-1'] = datetime.now
    tnc.monitor._on_receive_monitor(frame)


    pass




ip = {}

TNC2 = {}
tnc = TNC() 
tnc.kiss_interface = connect.kiss_interface (_on_receive, logging)



#input_loop()

streaming_queue = asyncio.Queue()


myeliza = {'Stream': 'H', 'Therapist': None}


def axReceived(text, ax):
    c = tnc.streams[ax].Connection

    cA = tnc.streams['A'].Connection
    cEliza = tnc.streams[myeliza['Stream']].Connection
    if not cA is None and not cEliza is None:
        # now check if our end is connected...
        # we must assume the other end is connected
        if c.axConnected:
            #c.axSend (text)
            True

    tnc.output ('AX%s> %s' % (ax, text))
    


def tncReceived(text, ax):
    c = tnc.streams[ax].Connection

        #c.axSend (myeliza['Therapist'].respond (text))
    if ax == myeliza['Stream']:
        c.axSend (myeliza['Therapist'].respond (text))
    else:
        tnc.output ('%s> %s' % (ax, text))

def axConnected(ax):
    loggerscreen.debug ('# axConnected %s ' % (ax))
    c = tnc.streams[ax].Connection

def tncConnected(ax):
    loggerscreen.debug ('# tncConencted %s' % (ax))
    c = tnc.streams[ax].Connection
    if 'UTC' in completer.options and completer.options['UTC'].Value:
        t = datetime.utcnow()
    else:
        t = datetime.now()


    if completer.options['CONSTAMP'].Value:
        tnc.output ('*** CONNECTED to %s %s' % (c.callTo, ip.displaydatetime(t)))
    else:
        tnc.output ('*** CONNECTED to %s' % (c.callTo))
    tnc.mode = tnc.modeConverse # Automatically go into CONVERSE mode

def axDisconnected(ax):
    c = tnc.streams[ax].Connection
    tnc.output ('*** AXDISCONNECTED')

def tncDisconnected(ax):
    c = tnc.streams[ax].Connection
    tnc.output ('*** DISCONNECTED %s' % (ax))
    tnc.mode = tnc.modeCommand
    # tnc.streams[ax] = None
    if ax == 'A':
        # also disconnect the far end if needed
        cEliza = tnc.streams[myeliza['Stream']].Connection
        cEliza.disconnect()


def axSend(text, ax):
    loggerscreen.debug ('# axSend %s %s ' %(text, ax))
    c = tnc.streams[ax].Connection

    cA = tnc.streams['A'].Connection # Assume A
    cEliza = tnc.streams[myeliza['Stream']].Connection 


    if ax == 'A':
        cEliza.axReceived (text)
    if ax == myeliza['Stream']:
        cA.axReceived (text)


        #c.axSend (myeliza['Therapist'].respond (text))

    True

def tncSend(text, ax):
    loggerscreen.debug ('# tncSend %s ' % (ax))
    c = tnc.streams[ax].Connection
    True





def axInit(ax):
    global myeliza
    loggerscreen.debug ('# axInit %s ' % (ax))

    c = tnc.streams[ax].Connection
    if not c is None: # Should never be none... But...
        if c.callTo == 'ELIZA':
            # we need to init another stream and connection. Lets call it H or Hell..
            # swap the callsigns
            callFrom = c.callTo
            callTo = c.callFrom
            callDigi = c.callDigi.reverse()
            myeliza['Therapist'] = eliza.Eliza()
            commands.connection (callFrom, callTo, callDigi, tnc.streams[myeliza['Stream']])


def tncInit(ax):
    loggerscreen.debug ('# tncInit %s ' % (ax))
    c = tnc.streams[ax].Connection
    if c.callTo == 'ELIZA': 
        cEliza = tnc.streams[myeliza['Stream']].Connection
        cEliza.connect = True



async def periodic():
    while True:
        if True:
            # Eliza functionality
            cA = tnc.streams['A'].Connection # Assume A
            cEliza = tnc.streams[eliza['Stream']].Connection
            if not cA is None and not cEliza is None:
                # we have connection objects on both
                if not cA.connected and not cEliza.connected:
                    # neither end is connected
                    if cA['callTo'] == cEliza['callFrom'] and cA['callFrom'] == cEliza['callTo']:
                        # we are trying to connect to each other definitely...
                        cA.connected = True
                        cEliza.connected = True


        await asyncio.sleep(1)





async def main_async():
    while True:
        chunk = await streaming_queue.get()
        if tnc.mode == tnc.modeCommand:
            
            r = ip.input_process(chunk)
            if r == commands.returns.Eh:
                tnc.output ('?EH')
            elif r == commands.returns.Bad:
                tnc.output ('?BAD')
            elif r == commands.returns.NotImplemented:
                tnc.output ('?Not Implemented')
        elif tnc.mode == tnc.modeConverse:
            if tnc.exitToCommandMode in chunk:
                tnc.mode = tnc.modeCommand
            elif chunk[:3].upper() == 'BYE' :
                tnc.streams['A'].Connection.disconnect()
            else:
                tnc.streams['A'].Connection.axSend(chunk)
            True
        elif tnc.mode == tnc.modeTrans:
            True

        semaphore.release()


def event_loop(loop):
    #Remove comments in production

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

def output (line):
    print ('%s' %(line))

def init():
    global completer
    global ip 
    global console

    tnc.output ('TAPR TNC2 Clone')
    tnc.output ('Copyright 2023 Darryl Smith, VK2TDS')
    tnc.output ('')

    


    tnc.on_Connect (tncConnected)
    tnc.on_Disconnect (tncDisconnected)
    tnc.on_Received (tncReceived)
    tnc.on_Sent (tncSend)
    tnc.on_Init (tncInit)

    tnc.on_axConnect (axConnected)
    tnc.on_axDisconnect (axDisconnected)
    tnc.on_axReceived (axReceived)
    tnc.on_axSent (axSend)
    tnc.on_axInit (axInit)



    for index in ROM.TNC2_ROM:
        c = commands.Individual_Command()
        c.set (ROM.TNC2_ROM[index])
        c.Display = index
        TNC2[index.upper()] = c

    # Register our completer function
    completer = commands.BufferAwareCompleter(TNC2, logging)

    tnc.monitor.setCompleter(completer)
    tnc.monitor.setOutput(output)
    tnc.monitor.setTnc(tnc)

    readline.set_completer(completer.complete)

    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('"ç": "%s\n"' % (tnc.exitToCommandMode))
 
    ip = commands.process (completer, tnc)

    # First, process defaults
    for o in completer.options:
        if completer.options[o].Default is not None:
            line = o + ' ' + completer.options[o].Default
            ip.input_process (line, display=False)
        # Only the upper case letters are an alternative
        completer.options[o].Shorter = ''.join(filter(str.isupper, completer.options[o].Display))

    # Custom startup for debugging...
    for custom in ('TRACE ON', 
                   'DAYUSA OFF', 
                   'CONSTAMP ON', 
                   'TRACE OFF',
                   'KISSdev 1 tcp localhost 8001',
                   'KISSPort 1 1'
                   ):
        ip.input_process (custom, display=True)


init()


semaphore = Semaphore()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    event_thread = Thread(target=event_loop, args=(loop,))
    event_thread.start()
    task = loop.create_task(periodic()) # every second 
    if True: 
            chunk = ''
            while chunk != 'stop':
                # GNU readline overloads input() 
                semaphore.acquire()

                if tnc.mode == tnc.modeCommand:
                    chunk = input('cmd: ')
                elif tnc.mode == tnc.modeConverse:
                    chunk = input('> ')
                elif tnc.mode == tnc.modeTrans:
                    chunk = input('> ')

                loop.call_soon_threadsafe(send_chunk, chunk)


