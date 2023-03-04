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
from aioax25.kiss import make_device
import aioax25
from aioax25.version import AX25Version



class kiss_interface():
    #ToDo: Split call from kiss_interface
    def __init__ (self, on_rx, logging):
        self.kissDevices = {}
        #self.ax25int = ax25int
        self.logging = logging
        self.loop = asyncio.get_event_loop()
        self.on_rx = on_rx
        self.call = ""
        self.ssid = 0

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
        self.kissDevices[dev] = {'Host': host, 'Port': port, 'Phy': 'tcp', 'Kiss': {} }
        kissdevice = self.start_ax25_device (host, port, 'TCP')
        self.kissDevices[dev]['KissDevice'] = kissdevice

    def kissPort (self, device, kissPort):
        dev = str(int(device))
        print ('Before Here')
        if dev in self.kissDevices:
            print ('Here')
            print (self.kissDevices[dev]['KissDevice'])
            axint = self.start_ax25_port (self.kissDevices[dev]['KissDevice'], kissPort)
            self.kissDevices[dev][str(kissPort)] = {'AX25Interface': axint,
                                                        'Station': None}

    def start_ax25_device(self, host, port, phy):

        if phy.upper() == 'TCP':
            
            kissdevice = make_device(
            type="tcp", host="localhost", port=8001,
            log=self.logging.getLogger("ax25.kiss"),
            loop=self.loop
            )
            kissdevice.open() # happens in background asynchronously
            return kissdevice
        self.logger.debug ('start_ax25_device - No TCP interface specified')


    def start_ax25_port(self, kissdevice, kissPort):

        #That `KISSDevice` class represents all the ports on the KISS interface
        #-- for Direwolf; there can be multiple ports (e.g. on my UDRC-II board,
        #the DIN-6 connector is port 1 and the DB15HD is port 0.).  Most
        #single-port TNCs only implement port 0:

        #kissport = kissdevice[0] # first KISS port on device

        ax25int = aioax25.interface.AX25Interface(
            kissport=kissdevice[int(kissPort)],         # 0 = HF; 2 = USB
            loop=self.loop, 
            log=self.logging.getLogger('ax25.interface')
        )

        ax25int.bind (self.on_rx, '(.*?)', ssid=None, regex=True)
        return ax25int


    def start_ax25_station(self, device, kissPort):

        #AX25Station takes AX25Interface as a constructor. [SSID on network]
        #attach interface via .attach() - links it up to an interface so it can send/receive S and I frames
        dev = str(int(device))
        axint = self.kissDevices[dev][str(kissPort)]


        station = aioax25.station.AX25Station (axint, self.call, 
                                            self.ssid, 
                                            protocol=AX25Version.AX25_20, 
                                            log=self.logging, 
                                            loop=self.loop)

        station.attach() # Connect the station to the interface

