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



try:
    import gnureadline as readline
except ImportError:
    import readline

import logging
import asyncio
import aioax25
import sys
import time
import traceback
import library


from aioax25.kiss import make_device
from aioax25.signal import Signal
from aioax25.interface import AX25Interface
from aioax25.frame import AX25UnnumberedInformationFrame
from aioax25.station import AX25Station
from aioax25.version import AX25Version

from threading import Thread
from threading import Semaphore
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime
from datetime import timezone
from datetime import timedelta

#local
import commands 
import connect 
import ROM

formater = logging.Formatter('%(name)-13s: %(levelname)-8s %(message)s')

LOG_FILENAME = '/tmp/pyTNC.log'
logging.basicConfig(
    format='%(name)-13s: %(levelname)-8s %(message)s',
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)

logger = logging.getLogger()
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_FILENAME)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
loggerfile = logging.getLogger('file')


console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)

console.setFormatter(formater)
logging.getLogger('console').addHandler(console)

loggerconsole = logging.getLogger ('console')

loggerfile.info ('')
loggerfile.info ('Starting pyTNC - Copyright 2023 Darryl Smith VK2TDS')


#TODO remove this tracefunc ???
def tracefunc(frame, event, arg, indent=[0]):
      # https://stackoverflow.com/questions/8315389/how-do-i-print-functions-as-they-are-called
      if event == "call":
          indent[0] += 2
          print("-" * indent[0] + "> call function", frame.f_code.co_name)
      elif event == "return":
          print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
          indent[0] -= 2
      return tracefunc
    # To activate sys.setprofile(tracefunc) 
if False: 
        sys.setprofile(tracefunc)


class TNC:
    def __init__(self):
        self.modeConverse = 0
        self.modeTransparent = 1
        self.modeCommand = 2
        self.tncMode = self.modeCommand
        self.station = None

        self.tncConnected = False
        self.mheard = {}
        self.kiss_interface = None
        self.exitToCommandMode = '*** COMMAND MODE ***'

        self.beaconCondition = 'AFTER'
        self.beaconPeriod = 0 # Beacon every 0 * 10 seconds
        self.beaconDue = 0

        self.monitor = commands.Monitor()
        self._completer = None


        self.streams = {}
        for s in commands.streamlist:
            self.streams[s] = connect.Stream(s, loggerfile)
            self.streams[s]._name = s

        self._currentStream = commands.streamlist[0]


    def receive(self):
        # An indication that we have receieved a packet with payload from over the air
        # This function can be called from a STREAM class, or can be called from a library when
        # the user changes stream.

        if self.activeStream._rxBuffer.qsize() > 0:
            toPrint = False
            if self.tncMode == self.modeCommand:
                toPrint = False
            elif self.tncMode == self.modeCommand:
                toPrint = True
            elif self.tncMode == self.modeTransparent:
                toPrint = True
            if toPrint:
                while not self.activeStream._rxBuffer.empty():
                    tnc.output (self.activeStream._rxBuffer.get()) #TODO add timeout?


    @property
    def completer (self):
        return self._completer
    
    @completer.setter
    def completer (self, c):
        self._completer = c
        for s in self.streams:
            self.streams[s].completer = self._completer 

    # These are letters
    @property 
    def currentStream(self):
        return self._currentStream
    
    @currentStream.setter
    def currentStream(self, s):
        self._currentStream = s

    # return the stream object.
    @property
    def activeStream (self):
        return self.streams[self._currentStream]


    def output (self, line):
        print (line)

    def sendID (self, port):
        frame = aioax25.frame.AX25UnnumberedInformationFrame(
            destination='ID',
            source=self._completer.options['MYCALL'].Value,
            repeaters=None, 
            pid=aioax25.frame.AX25Frame.PID_NO_L3,
            payload=str.encode(self._completer.options['IDTEXT'].Value)
        )

        self.kiss_interface.kissInts[port].transmit (frame)
        self.kiss_interface.kissIntsLastTX[port] = library.datetimenow(self._completer)

    def setBeacon (self, cond, period):
        self.beaconPeriod = int(period)
        if cond == 'AFTER':
            self.beaconCondition = 'AFTER'
            if self.beaconPeriod > 0:
                self.beaconDue = time.time() + 2 # if BEACON EVERY, send after 2 seconds
            else:
                self.beaconDue = 0
        else: # EVERY
            self.beaconCondition = 'EVERY'
            if self.beaconPeriod > 0:
                self.beaconDue = time.time() + self.beaconPeriod
            else:
                self.beaconDue = 0


    def PPSbeacon(self):
        # One pulse per second. Duh. Needs to be triggered of course.
        try:
            t = time.time()
            if self.beaconDue != 0:
                if self.beaconDue <= t:
                    #axint = self.kiss_interface.kissDevices['1'].KissPorts(0).AX25Interface

                    u = completer.options['UNPROTO'].Value.split()
                    dest = u[0]
                    r = None
                    if len(u) > 1:
                        u.pop (0)
                        if len(u) != 0:
                            r = u
 
                    frame = aioax25.frame.AX25UnnumberedInformationFrame(
                        destination=dest,
                        source=self._completer.options['MYCALL'].Value,
                        repeaters=r, 
                        pid=aioax25.frame.AX25Frame.PID_NO_L3,
                        payload=str.encode(self._completer.options['BTEXT'].Value)
                    )
                    print (frame)

                    self.kiss_interface.kissInts[self.kiss_interface.activeStream.Port].transmit (frame)

                    self.kiss_interface.kissIntsLastTX[self.kiss_interface.activeStream.Port] = library.datetimenow(self._completer) 


                    #axint.transmit (frame) #callback=None)

                    if self.beaconCondition == 'AFTER':
                        self.beaconDue = 0
                    else:
                        self.beaconDue = t + (self.beaconPeriod * 10) 
        except Exception:
            traceback.print_exc()

    def PPS(self):
        self.PPSbeacon()





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


def _on_receive(interface, frame, match=None):
    # NOTE: Make sure the kissdevice lines up with the one you wnat to listen too

    tnc.mheard[str(frame.header.source)] = library.datetimenow(completer)
    tnc.monitor._on_receive_monitor(interface, frame)




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
                tnc.output ('--->BYE')
                tnc.activeStream.disconnect()
            else:
                tnc.activeStream.send (chunk)
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



ip = None
tnc = None


streaming_queue = asyncio.Queue()



def init():
    global completer
    global ip 
    global tnc
    global console

    if not tnc is None:
        # we must be doing a power on reset!!!
        tnc.kiss_interface.closedown()
        tnc.output ('Power On Reset')
        del tnc


    tnc = TNC() 
    tnc.kiss_interface = connect.kiss_interface (tnc, _on_receive, loggerfile)

    tnc.output ('TAPR TNC2 Clone')
    tnc.output ('Copyright 2023 Darryl Smith, VK2TDS')
    tnc.output ('')

    TNC2 = {}



    for index in ROM.TNC2_ROM:
        c = commands.Individual_Command()
        c.set (ROM.TNC2_ROM[index])
        c.Display = index
        TNC2[index.upper()] = c

    # Register our completer function
    completer = commands.BufferAwareCompleter(TNC2, loggerfile)

    tnc.completer = completer
    tnc.monitor.completer = completer
    tnc.monitor.setOutput(output)
    tnc.monitor.setTnc(tnc)

    readline.set_completer(completer.complete)

    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('"ç": "%s\n"' % (tnc.exitToCommandMode)) # Alt-C / Option-C on MacOS depending on the keyboard 

    ip = commands.process (completer, tnc, init)

    # First, process defaults
    for stage in range (1,4): # Process defaults in stages. 1 is default, then 2, 3, etc. Needed for KissDev and KissPort
        for o in completer.options:
            if completer.options[o].Stage == stage:
                if completer.options[o].Default is not None:
                    line = o + ' ' + completer.options[o].Default
                    ip.input_process (line) # ignore the return values
                # Only the upper case letters are an alternative
                completer.options[o].Shorter = ''.join(filter(str.isupper, completer.options[o].Display))


    # Custom startup for debugging... Ideally the defaults elsewhere should be the defaults...
    # well, except for KISSdev and KISSPort, which can have multiple calls
    tnc.output ('Loading custom settings..')
    p = Path(__file__).with_name('custom.txt')
    if p.exists():
        #if os.path.isfile (filename):
        with p.open('r') as f:
            lines = f.readlines()
            for custom in lines:
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


