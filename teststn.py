#!/usr/bin/env python3

import logging
from asyncio import run, sleep
from aioax25.station import AX25Station
from aioax25.kiss import make_device
from aioax25.interface import AX25Interface
from pprint import pprint
import re
import aioax25

def _on_receive_trace (frame): 
    bytes = frame.__bytes__() 
    paclen = len(bytes)
    output (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
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
        output (line)



def _on_receive_monitor (interface, frame):


    port = interface._port
    device = 'Unknown'

 

    calls = re.split (r"[*>,]", str(frame.header))
    calls = [value for value in calls if value != '']


        
    callsigns = frame.header.source.__str__() + '>' + frame.header.destination.__str__() + ',' + frame.header.repeaters.__str__()

    if type(frame) is aioax25.frame.AX25RawFrame:
        output ('--->AX25RawFrame')
        output (frame)

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
    
    output (type(frame))
    output (frame)

    #ADRdisp - default ON - N4UQQ>N4UQR,TPA5* <UI R>:This is a monitored frame.
    if hasattr(frame, 'payload'):
        payload = str(frame.payload.decode())
    else:
        payload = '<NO_PAYLOAD>'


    out = callsigns + control + payload



    output (out)

    _on_receive_trace (frame)




def output(line):
    print (line)




def _on_connection_rq(peer, **kwargs):
    log = logging.getLogger("connection.%s" % peer.address)

    log.info("Incoming connection from %s", peer.address)

    def _on_state_change(state, **kwargs):
        log.info("State is now %s", state)
        if state is peer.AX25PeerState.CONNECTED:
            peer.send(("Hello %s\r\n" % peer.address).encode())
            peer.send(("Hello %s\r\n" % peer.address).encode())


    def _on_rx(payload, **kwargs):
        try:
            payload = payload.decode()
        except Exception as e:
            log.exception("Could not decode %r", payload)
            peer.send("Could not decode %r: %s", payload, e)
            return

        log.info("Received: %r", payload)
        peer.send(("You sent: %r\r\n" % payload).encode())
        peer.send(("You sent: %r\r\n" % payload).encode())
        if payload == "bye\r":
            peer.send(("Disconnecting\r\n").encode())
            peer.disconnect()

    peer.connect_state_changed.connect(_on_state_change)
    peer.received_information.connect(_on_rx)
    peer.accept()

def _on_rx (interface, frame, match=None):
    _on_receive_monitor (interface, frame)

async def asyncmain():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s[%(filename)s:%(lineno)4d] %(levelname)s %(message)s'
    )

    kissdev = make_device(
        type="tcp", host="localhost", port=8001,
        reset_on_close=False, kiss_commands=[]
    )
    interface = AX25Interface(kissdev[0])


    interface.bind (_on_rx, '(.*?)', ssid=None, regex=True)

    station = AX25Station(
        interface=interface,
        callsign="VK2TDS", ssid=2
    )

    station.connection_request.connect(_on_connection_rq) # Incoming
    station.attach()
    kissdev.open()

    station.getpeer ()

    logging.getLogger("asyncmain").info("Waiting for connections")

    try:
        while True:
            await sleep(10)
    except KeyboardInterrupt:
        pass

    station.detach()
    kissdev.close()


run(asyncmain())