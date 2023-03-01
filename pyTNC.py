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
from datetime import datetime

import commands 

import re



LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    format='%(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)














class TNC:


    def __init__(self):
        self.modeConverse = 0
        self.modeTransparent = 1
        self.modeCommand = 2
        self.tncMode = self.modeCommand

        self.tncConnected = False
        self.mheard = {}
        self.streams = {'A': {'Stream': 'A', 'Connection': None, 'cbDisconnect': [], 'cbReceived': [], 'cbSent': [], 'cbConnect': []}, 
                        'B': {'Stream': 'B', 'Connection': None, 'cbDisconnect': [], 'cbReceived': [], 'cbSent': [], 'cbConnect': []},  
                        'C': {'Stream': 'C', 'Connection': None, 'cbDisconnect': [], 'cbReceived': [], 'cbSent': [], 'cbConnect': []}, 
                        'D': {'Stream': 'D', 'Connection': None, 'cbDisconnect': [], 'cbReceived': [], 'cbSent': [], 'cbConnect': []}, 
                        'E': {'Stream': 'E', 'Connection': None, 'cbDisconnect': [], 'cbReceived': [], 'cbSent': [], 'cbConnect': []} }


    def on_Disconnect (self, cb):
        for s in ('A', 'B', 'C', 'D'):
            self.streams[s]['cbDisconnect'].append (cb)

    def on_Received (self, cb):
        for s in ('A', 'B', 'C', 'D'):
            self.streams[s]['cbReceived'].append (cb)
            
    def on_Sent (self, cb):
        for s in ('A', 'B', 'C', 'D'):
            self.streams[s]['cbSent'].append (cb)
            
    def on_Connect (self, cb):
        for s in ('A', 'B', 'C', 'D'):
            self.streams[s]['cbConnect'].append (cb)
        

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
    #print ('_on_receive')
    #print (frame.header)
    #print (frame.header.destination)
    #print (frame.header.source)
    #print (frame.header.repeaters)
    #print (frame.header.cr)     # cd = Command Response bit
    #print (frame.header.src_cr)
    #print ('Control %x' %(frame.control))
    #print (frame.pid)
    #print (frame.frame_payload)
    #print (frame)
    #print (str(type(frame)))
    #print (type(frame) is aioax25.frame.AX25UnnumberedInformationFrame)
    #https://stackoverflow.com/questions/70181515/how-to-have-a-comfortable-e-g-gnu-readline-style-input-line-in-an-asyncio-tas


    if 'UTC' in completer.options and completer.options['UTC']['Value']:
        tnc.mheard[str(frame.header.source)] = datetime.utcnow()
    else:
        tnc.mheard[str(frame.header.source)] = datetime.now()

    #tnc.mheard['VK2TDS-1'] = datetime.now
    commands._on_receive_monitor(frame, completer, tnc)







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
    kissport=kissdevice[1],         # 0 = HF; 2 = USB
    loop=loop, log=logging.getLogger('ax25.interface')
    )

    ax25int.bind (_on_receive, '(.*?)', ssid=None, regex=True)








ip = {}

TNC2 = {}
tnc = TNC() 


#input_loop()

streaming_queue = asyncio.Queue()


def tncReceived(text, ax):
    print ('R> %s' % (text))

def tncConnected(ax):

    if 'UTC' in completer.options and completer.options['UTC']['Value']:
        t = datetime.utcnow()
    else:
        t = datetime.now()


    if completer.options['CONSTAMP']['Value']:
        print ('*** CONNECTED to %s %s' % (tnc.streams[ax]['Connection'].callTo, ip.displaydatetime(t)))
    else:
        print ('*** CONNECTED to %s' % (ax.callTo))
    tnc.mode = tnc.modeConverse # Automatically go into CONVERSE mode


def tncDisconnected(ax):
    print ('*** DISCONNECTED')
    tnc.mode = tnc.modeCommand
    tnc.streams['A'] = None

def tncSend(text, ax):
    True
    #print ('Sent')


async def main_async():
    while True:
        chunk = await streaming_queue.get()
        if tnc.mode == tnc.modeCommand:
            
            r = ip.input_process(chunk)
            if r == commands.returns.Eh:
                print ('?EH')
            elif r == commands.returns.Bad:
                print ('?BAD')
            elif r == commands.returns.NotImplemented:
                print ('?Not Implemented')
        elif tnc.mode == tnc.modeConverse:
            if chunk[:3].upper() == 'BYE':
                tnc.streams['A']['Connection'].disconnect()
            else:
                tnc.streams['A']['Connection'].send(chunk)
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


def init():
    global completer
    global ip 

    print ('TAPR TNC2 Clone')
    print ('Copyright 2023 Darryl Smith, VK2TDS')
    print ('')


    tnc.on_Connect (tncConnected)
    tnc.on_Disconnect (tncDisconnected)
    tnc.on_Received (tncReceived)
    tnc.on_Sent (tncSend)


    for index in commands.TNC2_ROM:
        TNC2[index.upper()] = commands.TNC2_ROM[index]
        TNC2[index.upper()]['Display'] = index

    # Register our completer function
    completer = commands.BufferAwareCompleter(TNC2, logging)

    readline.set_completer(completer.complete)

    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')


    ip = commands.process (completer, tnc)

    # First, process defaults
    for o in completer.options:
        if 'Default' in completer.options[o]:
            line = o + ' ' + completer.options[o]['Default']
            ip.input_process (line, display=False)
        # Only the upper case letters are an alternative
        completer.options[o]['Shorter'] = ''.join(filter(str.isupper, completer.options[o]['Display']))

    # Custom startup for debugging...
    for custom in ('TRACE ON', 'DAYUSA OFF', 'CONSTAMP ON'):
        ip.input_process (custom, display=True)

    start_ax25()

init()

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