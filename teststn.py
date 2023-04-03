#!/usr/bin/env python3

import logging
from asyncio import run, sleep
from aioax25.station import AX25Station
from aioax25.kiss import make_device
from aioax25.interface import AX25Interface

def _on_connection_rq(peer, **kwargs):
    log = logging.getLogger("connection.%s" % peer.address)

    log.info("Incoming connection from %s", peer.address)

    def _on_state_change(state, **kwargs):
        log.info("State is now %s", state)
        if state is peer.AX25PeerState.CONNECTED:
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

        if payload == "bye\r":
            peer.send(("Disconnecting\r\n").encode())
            peer.disconnect()

    peer.connect_state_changed.connect(_on_state_change)
    peer.received_information.connect(_on_rx)
    peer.accept()


async def asyncmain():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s[%(filename)s:%(lineno)4d] %(levelname)s %(message)s'
    )

    kissdev = make_device(
        type="serial", device="/dev/ax0", baudrate=9600,
        reset_on_close=False, kiss_commands=[]
    )
    interface = AX25Interface(kissdev[0])
    station = AX25Station(
        interface=interface,
        callsign="VK4MSL", ssid=4
    )

    station.connection_request.connect(_on_connection_rq)
    station.attach()
    kissdev.open()

    logging.getLogger("asyncmain").info("Waiting for connections")

    try:
        while True:
            await sleep(10)
    except KeyboardInterrupt:
        pass

    station.detach()
    kissdev.close()


run(asyncmain())