# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in
progress, with lots more work needed. Thing such as error checking are rarely implemented. 

The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added
to allow settings to be stored for use at runtime. 

* Type 'HELP ALL' for information on all the commands. This needs to be longer.
* Exiting CONV mode is an issue at the moment. ALT-C on my Mac exits into command mode
* You can connect to Eliza by typing 'C ELIZA' at the CMD prompt. Exit by typing 'BYE'


== Notes on using the AIOAX25 library ==

AX25Station takes AX25Interface as a constructor. [SSID on network]
attach interface via .attach() - links it up to an interface so it can send/receive S and I frames

Incoming connections signalled via connection_request
handler is passed AX25Peer instance via peer keyword argument
- Call accept() to send a UA frame; or reject to send a DM frame

To make outbound connection call .get_peer() to get instance of AX25Peer for the remote station
Then call .connect() which will try sending XID (unless told it is ax25 2.0 before), followed by SABM or SABME

AX25Peer is supposed to buffer incoming stream and emit via received_information [Not yet implemented]

AX25Peer send is missing. Should be a `.send()` that basically buffers the outgoing traffic, slices it into
I-frames, and sends them.











Hi Darryl,

One thing with Python to watch out for: it is indentation sensitive.
Somewhere in the email system, that indentation got lost.  An
attachment might be safer in terms of preserving code formatting.

On Sun, 5 Mar 2023 00:29:02 +0000
Darryl Smith <darryl@radio-active.net.au> wrote:

Hi Stuart

I think I am getting somewhere with regards to understanding things.
Can you have a look over this code and see if I am going the right
way? Also, not sure about hooks for received_information and send. I
know they likely Havent been implemented yet, but it would be great
to see what I can implement

Yep, I'm open to ideas here because it hasn't been implemented yet, so
things are much more "pliable" than they would be if already written.
:-)

def start_ax25_station(self, device, kissPort):

#AX25Station takes AX25Interface as a constructor. [SSID on network]
#attach interface via .attach() - links it up to an interface so it
can send/receive S and I frames

dev = str(int(device))
axint = self.kissDevices[dev][str(kissPort)]

Took me a little while to figure what was going on here, at first I
thought `axint` was a `KISSDevice` for a moment, but I realise now it's
a `dict` container for some related objects.  Realistically a class
would be better for this to "tie" the objects together, but a `dict`
will certainly do for prototyping purposes.

station = aioax25.station.AX25Station (axint['AX25Interface'],
self.call, self.ssid,
protocol=AX25Version.AX25_20,
log=self.logging,
loop=self.loop)

Worth noting that `protocol` is optional here, and if not specified, it
defaults to `UNKNOWN` which will trigger auto-negotiation -- however
some TNCs do not handle auto-negotiation well, so forcing AX.25 2.0
isn't a bad option. :-)

station.attach() # Connect the station to the interface
axint['Station'] = station

peer = station.getpeer ('N0CALL', 0, []) # callsign, ssid, repeaters[]

These will default to 0 and no digipeaters if left off, only the
callsign is mandatory.

peer.connect()
axint['Peer'] = peer

def send_ax25_station (self, device, kissPort, data):
dev = str(int(device))
axint = self.kissDevices[dev][str(kissPort)]

peer = axint['Peer']

# **************
peer.send (data)
# **************

Now, at present there isn't a `def send(self, data):` method on
`AX25Peer`.  I'm thinking if there was, `data` should take `bytes` as
input (to send a string; call `.encode()` on it first), and it'll
buffer it for segmentation and transmission.

Likewise, `received_information` could return back raw bytes from the
I-frame payload, and/or it could hand back the incoming I-frame.
`signalslot` is the implementation used for implementing these signals,
and it works entirely through keyword arguments.  So I'm thinking that
whatever is "connected" to `received_information` should be able to accept
these keyword arguments (if a callback is not interested, it can use
`**kwargs` at the end to 'swallow' the things it's not interested in):

- `station`: `AX25Station` instance receiving the traffic
- `peer`: `AX25Peer` from whom the traffic was received from
- `frame`: The `AX25InformationFrame` containing the payload
- `data`: The receive buffer content (`bytes`), which can be empty

The thinking that `data` is any _new_ data received, discounting
de-duplications and out-of-order transmissions: if `data` is an empty
byte string, then the I-frame received pertains to out-of-order data
that has either already been seen or follows a frame that hasn't been
seen yet.

As I say, I'm open to ideas here.  This is meant to be a fairly
low-level interface that would then be overlaid by a higher-level
interface that mimics the interface used for things like TCP and serial
(AX.25 connected mode becomes "just another `asyncio` transport).  But,
you know the saying, learn to crawl before attempting to walk or run.
:-)

Regards,
-- 