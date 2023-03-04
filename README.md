# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in
progress, with lots more work needed. Thing such as error checking are rarely implemented. 

The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added
to allow settings to be stored for use at runtime. 

* Type 'HELP ALL' for information on all the commands. This needs to be longer.
* Exiting CONV mode is an issue at the moment. ALT-C on my Mac exits into command mode
* You can connect to Eliza by typing 'C ELIZA' at the CMD prompt. Exit by typing 'BYE'




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

