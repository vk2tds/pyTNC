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

import queue 
import asyncio
import aioax25
from aioax25.kiss import make_device
from aioax25.version import AX25Version

import logging
import commands 
import library 


class PeerStream():
    '''
    Connecting a PEER to a STREAM

    Links to a Stream Name
    '''

    def __init__(self, tnc):
        #print ('PEERSTREAM')
        self._peerStream = {}
        self._tnc = tnc 


    def linkname (self, peer):
        # Their end = peer.address
        # Our end = peer._station().address
        # Therefore, uniqueness === 

        return str(peer.address) + ':' + str(peer._station()._address)

    def whichstream (self, peer):
        linkname = self.linkname (peer)

        # if this peer is NOT connected to a stream, make it conencted to the current stream
        if not linkname in self._peerStream:
            if not self._tnc.currentStream in self._peerStream:
                # There is a slot in the curren stream
                self._peerStream[linkname] = self._tnc.currentStream
            else:
                # there is no slot in the current stream. Therefore, we need to find a space...
                freeStream = None
                for stream in commands.streamlist:
                    if not stream in self._peerStream:
                        freeStream = stream
                if freeStream is None:
                    # There are no slots available in streams. So dont assign this peer to a stream
                    return None
                self._peerStream[linkname] =  freeStream # Connect this peer to a stream
        # Since this peer is conencted to a stream, either because it was or because we made it, we
        # can return it. 
        return self._peerStream[linkname]
        
    def disconnect (self, peer):
        # remove the linking
        linkname = self.linkname (peer)
        if linkname in self._peerStream:
            self._peerStream.pop(linkname)


class Stream:
    def __init__(self, stream, logging):
        self._stream = stream 
        self._Port = None
        self._logging = logging 
        self._completer = None 
        self._peer = None
        self._name = None # The text name of this stream.
        self._state = None


        # incoming and outgoing buffers
        # for FIFO, use .put() and .get()
        #
        #TODO expand buffer sizes dynamically saving content
        
        self._bufferSize = 7            
        self._rxBuffer = queue.Queue(self._bufferSize)
        # Peer details

        self._peer = None


    def received (self, payload):
        if not self._rxBuffer.full():
            self._rxBuffer.put(payload)    
        else:
            # Not sure what to do if RX buffer is full.
            True
        # TODO Send a message somwehere to say that we have the payload. Investigate stream swapping

    def send (self, payload):
        if not self.peer is None:
            if self._completer.options['CR'].Value:
                pay = (payload + '\r').encode()
            else:
                pay = payload.encode()
            if self._completer.options['8BITCONV'].Value:
                pay = bytearray(pay) 
                for i in range(len(pay)):
                    pay[i] = pay[i] & 0x7f
            self._peer.send(pay)
        else:
            print ('*** NOT CONENCTED FOR ACTUAL STREAM SEND')

    def disconnect(self):
        if not self.peer is None:
            self._peer.disconnect()


    @property
    def peer(self):
        return self._peer

    @peer.setter
    def peer(self, apeer):
        self._peer = apeer


    @property
    def completer (self):
        return self._completer
    
    @completer.setter
    def completer (self, c):
        self._completer = c

    @property
    def state (self):
        return self._state
    
    @state.setter
    def state (self, c):
        self._state = c

    @property
    def Stream(self):
        return self._stream

    @property 
    def Port(self):
        return self._Port

    @Port.setter
    def Port(self, port):
        self._Port = port





class kiss_interface():
    #ToDo: Split call from kiss_interface
    def __init__ (self, tnc, on_rx, logging):
        self._kissDevices = {}
        self._kissInts = {}
        self._stations = {}
        self.logging = logging
        self.loop = asyncio.get_event_loop()
        self._on_rx = on_rx
        self.call = ""
        self.ssid = None
        self._myCall = ""
        self._mySsid = None
        self._tnc = tnc
        self._peerstream = PeerStream(self._tnc)

    def callsign(self, call):
        if '-' in call:
            (c,s) = call.split ('-')
            self.call = c
            self.ssid = int(s)
        else:
            self.call = c
            self.ssid = None

    def myCallsign(self, call):
        if '-' in call:
            (c,s) = call.split ('-')
            self._myCall = c
            self._mySsid = int(s)
        else:
            self._myCall = c
            self._mySsid = None

    def kissDeviceTCP (self, device, host, port):
        self._kissDevices[device] = make_device(
            type="tcp", host=host, port=port,
            log=self.logging, #.getLogger("ax25.kiss"),
            loop=self.loop
            )
        
        self._kissDevices[device].open() # happens in background asynchronously

    def kissDeviceSerial (self, device, baud, reset_on_close=False):
        self._kissDevices[device] = make_device(
            type="serial", device=device, baudrate=baud,
            log=self.logging, #.getLogger("ax25.kiss"),
            loop=self.loop
            )
        
        self._kissDevices[device].open() # happens in background asynchronously

    def kissPort (self, interface):
            if not interface in self._kissInts:
                (device,kissPort) = interface.split(':')
                self._kissInts[interface] = aioax25.interface.AX25Interface(
                    kissport=self._kissDevices[device][int(kissPort)],         # 0 = HF; 2 = USB
                    loop=self.loop, 
                    log=self.logging,
                )

            self._kissInts[interface].bind (self._on_rx, '(.*?)', ssid=None, regex=True)

            # when we open a KISSport, also open a STATION. 
            # TODO What happens when the callsign changes
            station = aioax25.station.AX25Station (self._kissInts[interface], 
                                    self._myCall, 
                                    self._mySsid, 
                                    protocol=AX25Version.AX25_20, 
                                    log=self.logging, 
                                    loop=self.loop)

            station.connection_request.connect(self._on_connection_rq) # incoming
            station.attach() # Connect the station to the interface
            self._stations[interface] = station


    @property 
    def kissInts(self):
        return self._kissInts


    @property
    def kissDevices(self):
        return self._kissDevices
            


    def _on_connection_rq(self, peer, **kwargs):
        log = logging.getLogger("connection.%s" % peer.address)

        log.info("Incoming connection from %s", peer.address)
        mystreamname = self._peerstream.whichstream(peer) # TODO fix to self
        mystream = self._tnc.streams[mystreamname]

        def _on_state_change(state, **kwargs):
            nonlocal mystream
            mystream.state = state
            log.info("State is now %s", state)
            constamp = self._tnc.completer.options['CONSTAMP'].Value
            cbell = self._tnc.completer.options['CBELL'].Value
            if state is peer.AX25PeerState.CONNECTING:
                mystream.peer = peer # I *THINK* I want to connect peer at this point so I could send data ready to go out.
                print ('----> CONNECTING')
            elif state is peer.AX25PeerState.CONNECTED:
                mystream.peer = peer
                message = '*** CONNECTED TO ' + str(peer.address) #TODO: Add DIGIPEATER ADDRESSES
                if constamp:
                    message = message + ' ' + library.displaydatetime (library.datetimenow(self._tnc.completer), self._tnc.completer)
                if cbell:
                    message = message + '\a' # Termainals often have the BELL silenced

                print (message)

                cmsg = self._tnc.completer.options['CMSG'].Value
                if cmsg == True or cmsg.upper() == 'DISC':
                    ctext = self._tnc.completer.options['CTEXT'].Value
                    if len(ctext) > 0:
                        mystream.send (ctext)
                    if cmsg.upper() == 'DISC':
                        peer.disconnect()

            elif state is peer.AX25PeerState.DISCONNECTING:
                mystream.peer = None # I *THINK* this is what I want here.
                message = message + ' ' + library.displaydatetime (library.datetimenow(self._tnc.completer), self._tnc.completer)
            elif state is peer.AX25PeerState.DISCONNECTED:
                mystream.peer = None
                message = '*** DISCONNECTED '
                if constamp: 
                    message = message + ' ' + library.displaydatetime (library.datetimenow(self._tnc.completer), self._tnc.completer)
                print (message)

        def _on_rx(payload, **kwargs):
            nonlocal mystream
            print ('RECEIVE')
            try:
                payload = payload.decode()
            except Exception as e:
                log.exception("Could not decode %r", payload)
                mystream.send("Could not decode %r: %s" % (payload, e))
                return

            self._peerstream.received (payload)


            #TODO: Do I need a TX buffer? Is it in the peer.send object?

            log.info("Received: %r", payload)
            mystream.send(("You sent: %r\r\n" % payload))

            if payload == "bye\r":
                mystream.send(("Disconnecting\r\n"))
                peer.disconnect()

        peer.connect_state_changed.connect(_on_state_change)
        peer.received_information.connect(_on_rx)
        peer.accept()


    # *********************************************
    # THIS FOLLOWING CODE IS NOT YET ACTIVE
    # *********************************************


    def connect_ax25_station(self, device, kissPort):

        dev = str(int(device))
        axint = self.kissDevices[dev].KissPorts(kissPort)


        # Is the following code for an outgoing connection?
        peer = axint.station.getpeer ('N0CALL', 0, []) # callsign, ssid, repeaters[]
        axint.axint.Peer = peer

        peer.connect()



    def send_ax25_station (self, device, kissPort, data):
        dev = str(int(device))
        axint = self.kissDevices[dev].KissPorts(kissPort)

        peer = axint.Peer

        # **************
        peer.send (data)
        # **************


