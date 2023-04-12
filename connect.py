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


import asyncio
import aioax25
from aioax25.kiss import make_device
from aioax25.version import AX25Version

import logging
import commands 

import queue 






class PeerStream():
    '''
    Connecting a PEER to a STREAM

    Links to a Stream Name
    '''

    def __init__(self, tnc):
        
        self._peerStream = {}
        self._tnc = tnc 


    def linkname (self, peer):
        # Their end = peer.address
        # Our end = peer._station().address
        # Therefore, uniqueness === 

        return peer.address + ':' + peer.station().address

    @property
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
        self._Connection = None

        self._Port = None
        self._logging = logging 

        self._cbDisconnect = [] # user callbacks
        self._cbReceived = []
        self._cbSent = []
        self._cbConnect = []
        self._cbInit = []
        self._axDisconnect = [] # ax25 callbacks
        self._axReceived = []
        self._axSent = []
        self._axConnect = []
        self._axInit = []



        # incoming and outgoing buffers
        # for FIFO, use .put() and .get()
        #
        #TODO expand buffer sizes dynamically saving content
        
        self._bufferSize = 7            
        self._rxBuffer = queue.Queue(self._bufferSize)
        self._txBuffer = queue.Queue(self._bufferSize)

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
            self._peer.send (payload)
        True

    @property
    def peer(self):
        return self._peer

    @peer.setter
    def peer(self, peer):
        self._peer = peer


    @property
    def Stream(self):
        return self._stream

    @property
    def Connection(self):
        return self._Connection
    
    @Connection.setter
    def Connection(self, connection):
        self._Connection = connection

    @property
    def cbDisconnect(self):
        return self._cbDisconnect
    
    @cbDisconnect.setter
    def cbDisconnect(self, cb):
        self._cbDisconnect.append (cb)

    @property
    def cbReceived(self):
        return self._cbReceived
    
    @cbReceived.setter
    def cbReceived(self, cb):
        self._cbReceived.append (cb)

    @property
    def cbSent(self):
        return self._cbSent
    
    @cbSent.setter
    def cbSent(self, cb):
        self._cbSent.append (cb)

    @property
    def cbConnect(self):
        return self._cbConnect
    
    @cbConnect.setter
    def cbConnect(self, cb):
        self._cbConnect.append (cb)

    @property
    def cbInit(self):
        return self._cbInit
    
    @cbInit.setter
    def cbInit(self, cb):
        self._cbInit.append (cb)

    @property
    def axDisconnect(self):
        return self._axDisconnect
    
    @axDisconnect.setter
    def axDisconnect(self, cb):
        self._axDisconnect.append (cb)

    @property
    def axReceived(self):
        return self._axReceived
    
    @axReceived.setter
    def axReceived(self, cb):
        self._axReceived.append (cb)

    @property
    def axSent(self):
        return self._axSent
    
    @axSent.setter
    def axSent(self, cb):
        self._axSent.append (cb)

    @property
    def axConnect(self):
        return self._axConnect
    
    @axConnect.setter
    def axConnect(self, cb):
        self._axConnect.append (cb)

    @property
    def axInit(self):
        return self._axInit
    
    @axInit.setter
    def axInit(self, cb):
        self._axInit.append (cb)

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
        print ('Callsign', call)
        if '-' in call:
            (c,s) = call.split ('-')
            self.call = c
            self.ssid = int(s)
        else:
            self.call = c
            self.ssid = None

    def myCallsign(self, call):
        print ('Callsign', call)
        if '-' in call:
            (c,s) = call.split ('-')
            self._myCall = c
            self._mySsid = int(s)
        else:
            self._myCall = c
            self._mySsid = None



    def kissDeviceTCP (self, device, host, port):
        print ('device', device)
        self._kissDevices[device] = make_device(
            type="tcp", host=host, port=port,
            log=self.logging, #.getLogger("ax25.kiss"),
            loop=self.loop
            )
        
        self._kissDevices[device].open() # happens in background asynchronously


    def kissPort (self, interface):
            if not interface in self._kissInts:
                (device,kissPort) = interface.split(':')
                print ('Adding here')
                self._kissInts[interface] = aioax25.interface.AX25Interface(
                    kissport=self._kissDevices[device][int(kissPort)],         # 0 = HF; 2 = USB
                    loop=self.loop, 
                    log=self.logging, #.getLogger('ax25.interface')
                )

            print ('Pre')
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

            self._kissInts[interface] = station

                

    @property 
    def kissInts(self):
        return self._kissInts


    @property
    def kissDevices(self):
        return self._kissDevices
            


    def _on_connection_rq(self, peer, **kwargs):
        log = logging.getLogger("connection.%s" % peer.address)

        log.info("Incoming connection from %s", peer.address)
        mystream = self.parentself._peerstream.whichstream(peer) # TODO fix to self


        def _on_state_change(state, **kwargs):
            nonlocal mystream
            print ('STATE')
            log.info("State is now %s", state)
            if state is peer.AX25PeerState.CONNECTING:
                self._peerstream.peer = peer # I *THINK* I want to connect peer at this point so I could send data ready to go out.
                True
            elif state is peer.AX25PeerState.CONNECTED:
                self._peerstream.peer = peer
                # print ('---->', peer.address + ':' + peer.station().address)

                peer.send(("Hello %s\r\n" % peer.address).encode())
            elif state is peer.AX25PeerState.DISCONNECTING:
                self._peerstream.peer = None # I *THINK* this is what I want here.

            elif state is peer.AX25PeerState.DISCONNECTED:
                self._peerstream.peer = None


        def _on_rx(payload, **kwargs):
            nonlocal mystream
            print ('RECEIVE')
            try:
                payload = payload.decode()
            except Exception as e:
                log.exception("Could not decode %r", payload)
                peer.send("Could not decode %r: %s", payload, e)
                return

            self._peerstream.received (payload)


            #TODO: Do I need a TX buffer? Is it in the peer.send object?

            log.info("Received: %r", payload)
            peer.send(("You sent: %r\r\n" % payload).encode())

            if payload == "bye\r":
                peer.send(("Disconnecting\r\n").encode())
                peer.disconnect()

        peer.connect_state_changed.connect(_on_state_change)
        peer.received_information.connect(_on_rx)
        peer.accept()




    # *********************************************
    # THIS FOLLOWING CODE IS NOT YET ACTIVE
    # *********************************************



    def start_ax25_station(self, interface, call, ssid):

        #AX25Station takes AX25Interface as a constructor. [SSID on network]
        #attach interface via .attach() - links it up to an interface so it can send/receive S and I frames

        print ('start_ax25_station')
        print (call)
        print (ssid)
        station = aioax25.station.AX25Station (self._kissInts[interface], 
                                            call, 
                                            ssid, 
                                            protocol=AX25Version.AX25_20, 
                                            log=self.logging, 
                                            loop=self.loop)

        station.connection_request.connect(self._on_connection_rq) # incoming
        station.attach() # Connect the station to the interface

        #TODO Where do stations get stored? Streams? On the current stream?
        #self.tnc.activeStream.Port

        # Do we need to split here... have a listen and have a talk?
        # Listen...


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


