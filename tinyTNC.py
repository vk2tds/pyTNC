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

# tinyTNC - This is code to test underlying AX25 structures before I then integrate them in the main softare




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
from aioax25.station import AX25Station
from aioax25.version import AX25Version

from threading import Thread
from datetime import datetime
from datetime import timezone
import time

from threading import Semaphore



import connect 
import mon


LOG_FILENAME = '/tmp/pyTNC.log'
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



class config():

    def __init__(self):
        self.mycall = 'VK2TDS-1'
        self.version = 'AXVERSION AX25_20'




                           , #for testing
                   'MYCALL vk2tds-2', 
                   'KISSdev 1 tcp localhost 8001',
                   'KISSPort 1 0'








async def periodic():
    while True:
        if tnc:
            tnc.PPS() # call TNC 1PPS



        await asyncio.sleep(1)





async def main_async():
    while True:
        chunk = await streaming_queue.get()
        if tnc.mode == tnc.modeCommand:
            ret = ip.input_process(chunk)
            r = ret[0]
            
            if r == commands.returns.Ok:
                if ret[1]: tnc.output (ret[1])
            elif r == commands.returns.Eh:
                if ret[1]: 
                    tnc.output ('?Eh %s' % ret[1])
                else:
                    tnc.output ('?EH')
            elif r == commands.returns.Bad:
                if ret[1]: 
                    tnc.output ('?Bad %s' % ret[1])
                else:
                    tnc.output ('?Bad')
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


def initStation (self, device, port):
    print ('initStart')
    try:
        axint = tnc.kiss_interface.kissDevices[str(device)].KissPorts(port).AX25Interface

        mycall = completer.options['MYCALL'].Value
        if '-' in mycall:
            (call, ssid) = mycall.split('-')
        else:
            call = mycall
            ssid = 0
        axver = AX25Version[completer.options['AXVERSION'].Value]
        self.station = AX25Station (axint, call, ssid, protocol = axver) # do the connection
        self.station.attach()
    except Exception:
        traceback.print_exc()


def _on_receive(interface, frame, match=None):
    # NOTE: Make sure the kissdevice lines up with the one you wnat to listen too


    #tnc.mheard['VK2TDS-1'] = datetime.now
    tnc.monitor._on_receive_monitor(frame)


def start():
    global kiss_interface

    kiss_interface = connect.kiss_interface (_on_receive, logging)
    #  'KISSdev 1 tcp localhost 8001',
    kiss_interface.kissDeviceTCP (1, 'localhost', 8001)
    # 'KISSPort 1 0'
    kiss_interface.kissPort (1, 0)
    initStation (int (words[1]), int (words[2]))



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
    readline.parse_and_bind('"ç": "%s\n"' % (tnc.exitToCommandMode)) # Alt-C / Option-C on MacOS depending on the keyboard 

    ip = commands.process (completer, tnc)

    # First, process defaults
    for o in completer.options:
        if completer.options[o].Default is not None:
            line = o + ' ' + completer.options[o].Default
            ip.input_process (line) # ignore the return values
        # Only the upper case letters are an alternative
        completer.options[o].Shorter = ''.join(filter(str.isupper, completer.options[o].Display))

    # Custom startup for debugging... Ideally the defaults elsewhere should be the defaults...
    # well, except for KISSdev and KISSPort, which can have multiple calls
    tnc.output ('Custom settings..')
    for custom in ('TRACE ON', 
                   'DAYUSA OFF', 
                   'CONSTAMP ON', 
                   'TRACE OFF',
                   'AXVERSION AX25_20', #for testing
                   'MYCALL vk2tds-2', 
                   'KISSdev 1 tcp localhost 8001',
                   'KISSPort 1 0'
                   ):
        ret = ip.input_process (custom)
        print (ret[1])
    print('')

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






