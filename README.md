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
