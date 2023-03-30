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



class Stream:
    def __init__(self, stream):
        self._stream = stream 
        self._Connection = None
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
        True
    
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

class KissDevices:
    def __init__ (self, host, port, phy):
        self._Host = host
        self._Port = port
        self._Phy = phy
        self._KissDevice = {}
        self._KissPorts = {}

    @property
    def Host(self):
        return self._Host
    
    @Host.setter
    def Host(self, host):
        self._Host = host

    @property
    def Port(self):
        return self._Port
    
    @Port.setter
    def Port(self, port):
        self._Port = port

    @property
    def Phy(self):
        return self._Phy
    
    @Port.setter
    def Phy(self, phy):
        self._Phy = phy

    @property
    def KissDevice(self):
        return self._KissDevice
    
    @KissDevice.setter
    def KissDevice(self, kissdevice):
        self._KissDevice = kissdevice

    def setKissPorts (self, port, kissports):
        self._KissPorts[port] = kissports

    def KissPorts (self, port):
        return self._KissPorts[port]
        

class KissPort:
    def __init__(self, axint, station, peer):
        self._AX25Interface = axint
        self._Station = station
        self._Peer = peer

    @property
    def AX25Interface (self):
        return self._AX25Interface
    
    @AX25Interface.setter
    def AX25Interface (self, axint):
        self._AX25Interface = axint

    @property
    def Station (self):
        return self._Station
    
    @Station.setter
    def Station (self, station):
        self._Station = station

    @property
    def Peer(self):
        return self._Peer
    
    @Peer.setter
    def Peer(self, peer):
        self._Peer = peer
        


#self.kissDevices[dev] = {'Host': host, 'Port': port, 'Phy': 'tcp', 'Kiss': {} }

class kiss_interface():
    #ToDo: Split call from kiss_interface
    def __init__ (self, on_rx, logging):
        self.kissDevices = {}
        #self.ax25int = ax25int
        self.logging = logging
        self.loop = asyncio.get_event_loop()
        self.on_rx = on_rx
        self.call = ""
        self.ssid = None
        self.myCall = ""
        self.mySsid = None


    def callsign(self, call):
        if '-' in call:
            (c,s) = call.split ('-')
            self.call = c
            self.ssid = int(s)
        else:
            self.call = c
            self.ssid = 0

    def kissDeviceTCP (self, device, host, port):
        dev = str(int(device))
        self.kissDevices[dev] = KissDevices (host, port, 'TCP')
        self.kissDevices[dev].KissDevice = self.start_ax25_device (host, port, 'TCP')

    def kissPort (self, device, kissPort):
        dev = str(int(device))
        if dev in self.kissDevices:
            axint = self.start_ax25_port (self.kissDevices[dev].KissDevice, kissPort)
            self.kissDevices[dev].setKissPorts (kissPort, KissPort (axint, None, None))
            #self.start_ax25_station (dev, kissPort)



            

    

    def start_ax25_device(self, host, port, phy):
        print ('start_ax25_device')
        if phy.upper() == 'TCP':
            
            kissdevice = make_device(
            type="tcp", host="localhost", port=8001,
            log=self.logging, #.getLogger("ax25.kiss"),
            loop=self.loop
            )
            kissdevice.open() # happens in background asynchronously

            return kissdevice
        self.logger.debug ('start_ax25_device - No TCP interface specified')


    def start_ax25_port(self, kissdevice, kissPort):
        print ('start_ax25_port')
        #That `KISSDevice` class represents all the ports on the KISS interface
        #-- for Direwolf; there can be multiple ports (e.g. on my UDRC-II board,
        #the DIN-6 connector is port 1 and the DB15HD is port 0.).  Most
        #single-port TNCs only implement port 0:

        #kissport = kissdevice[0] # first KISS port on device

        ax25int = aioax25.interface.AX25Interface(
            kissport=kissdevice[int(kissPort)],         # 0 = HF; 2 = USB
            loop=self.loop, 
            log=self.logging, #.getLogger('ax25.interface')
        )

        ax25int.bind (self.on_rx, '(.*?)', ssid=None, regex=True)
        return ax25int


    # *********************************************
    # THIS FOLLOWING CODE IS NOT YET ACTIVE
    # *********************************************



    def _on_connection_rq(self, peer, **kwargs):

        self.logging.info ('*** Connection Request in connect.py')

        # Accept the connection
        peer.accept()
        # do something else with peer here
        



    def start_ax25_station(self, device, kissPort, call, ssid):

        #AX25Station takes AX25Interface as a constructor. [SSID on network]
        #attach interface via .attach() - links it up to an interface so it can send/receive S and I frames
        dev = str(int(device))
        axint = self.kissDevices[dev].KissPorts(kissPort)

        print ('start_ax25_station')
        print (call)
        print (ssid)
        print (self.logging)
        self.logging.info ('TEST IF LOGGING WORKS')
        self.logging.getChild('a').info ('CHILD')
        station = aioax25.station.AX25Station (axint.AX25Interface, 
                                            call, 
                                            ssid, 
                                            protocol=AX25Version.AX25_20, 
                                            log=self.logging, 
                                            loop=self.loop)

        station.attach() # Connect the station to the interface
        axint.Station = station


        station.connection_request.connect(self._on_connection_rq)

        # Do we need to split here... have a listen and have a talk?
        # Listen...

        #def _on_connection_rq(peer, **kwargs):
        #   # Accept the connection
        #   peer.accept()
        #   # do something else with peer here
        #
        #station.connection_request.connect(_on_connection_rq)


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


