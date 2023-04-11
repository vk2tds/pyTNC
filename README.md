# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in
progress, with lots more work needed. Thing such as error checking are rarely implemented. 

The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added
to allow settings to be stored for use at runtime. 

The first thing that you should note is that custom settings are stored in the same directory as the code. These are user settings and 
work exactly as if they had been typed on the pyTNC command line. The file is called 'custom.txt'

The software has a command line GUI. At some point, a TCP interface would be cool, so that you could telnet in remotely. We are not to that point yet. The 
commands are basically TNC-2, with changes. They should all be documented if you type 'HELP ALL'. You can also get help with a command by replacing 'ALL'
with the name of the command. For instance 'HELP CONNECT' will tell you how to connect. This help does need to be expanded. 

The command to exit CONV mode is an issue at the moment. ALT-C on my Mac exits into command mode

== Changing the Callsign ==

To set the callsign, use 'MYCALL VK2TDS-10', replacing my callsign with your callsign obviously. The callsign should be set before you use the KISS commands below. In future this will likely be fixed. Therefore, at this point, work out how to connect to the TNC.



== Connecting to a TNC == 

At the moment, the software is required to connect to a KISS TNC via TCP. More connection modes will come. Since I am using a Mac, this is what I need
to use. There are two very important KISS commands that need to be used, KISSDEV and KISSINT. KISSDEV should be used first, since it sets up the device, followed by KISSINT, which sets up the interface on that device. 

An example appears below:

* KISSdev picopacket tcp localhost 8001
* KISSInt picopacket 0

Looking at the KISSDEV line, the first thing to note is the name 'picopacket'. This is freeform text. The only requirement is that it is the same as the ones used in KISSINT.

We then go to TCP, indicating that we are connecting via TCP. Then onto the hostname and port for the KISS interface. This is fairly straightforward.

Each KISS device can have miltiple interfaces. An interface is generally a radio port. These start at index 0, and go up from there. 

The KISSINT command basically just says which KISS interfaces to activate. 

You can see what has been set up by just typing the commands 'KISSINT' and 'KISSDEV'. However, a better way is using the 'PORT' command.

There needs to be a default interface for us to use. To make things easy, we use the 'PORT' command to see the available ports and select a new one. A port might be called something like 'picopacket:0'. To change to that port, type 'PORT picopacket:0'. If there is an asterisk next to one of the ports, that means it is the currently selected port. You can ignore the asterisk if changing ports.






== AX25 Version ==

To change the version of AX.25 being used, use the 'AXVERSION' command. It is slightly non-standard, as it only changes between AX.25v2.0 and AX.25v2.2. The default is the more modern version. To change to AX.25v2.0, you can use the command 'AXVERSION AX25_20'. 






== Streams ==

At the time of writing, streams are still being developed. You can see the current stream by typing 'STREAM' and change streams with the stream command followed by a character, for instance, 'STREAM B'. 

PORTS and CONNECTIONS operate within a stream. Connections stay in their current state when you change streams. When you return to a stream, it is as if you had never left it. 

There is a new command called 'STREAMSHOW', which when active, will display the stream when monitoring packets. Beware, this command may be changed to 'PORTSHOW' as the concept of streams is further developed. 
















TODO: have the custom.txt search in the home directory for the user too
TODO: Take over Control-C
TODO: Changing callsign after KISS is opened.
TODO: KISSDEV name case insenstive 
TODO: should it be STREAMSHOW or PORTSHOW??



== CODE ==



=== ROM.PY ===
All the TNC commands, default values, help and more are stored in ROM.py. This file is processed by being read into a class. Certain values are then over-ridden by the custom.txt file entries. 


=== commands.py ===

This file does a lot of heavy lifting. 

Firstly, it contains a class (Individual_Command) that stores all the details from ROM.py. Then it contains classes for processing commands - A Buffer Aware Completer class and an input processing class.

There is also a class to display packet dumps. This is in this file since most UI is done in this file.

Finally, thee is the 'connection' class that might not end up being used. In all honesty, I am trying to find a way to remove this code. 





* You can connect to Eliza by typing 'C ELIZA' at the CMD prompt. Exit by typing 'BYE'
* Over time functionality is added to pyTNC.py and then over time moved to another library. This code is very much being worked on

* I have disconnected ELIZA at the moment. She *MIGHT* be connected back in the future. 

* Look at the following commands
    #MFILTER Comma separated characters to totally ignore
    #MSTAMP WB9FLW>AD7I,K9NG*,N2WX-71 05/24/97 16:53:19]:Hi Paul.
    #UTC - display in UTC. Default OFF

    #MONITOR - 1 = No characters > 0x7F; 2 = MONITOR ON


    #CONRPT - if on, LTEXT -> L3TEXT, STEXT, CTEXT (if CMSG = On) sent on connection
    #    break if CMSGDISC????

    #CPOLL?
    #CSTATUS - Status of connection streams
    #CTEXT
    #DGPscall
    #Digipeat - Complex
    #EBEACON - Default OFF - BTEXT echoed to terminal on transmission
    #ENCRYPT, ENSHIFT
    #Group - default Off - group monitoring (MASTERM) - Ignore this command

    #STATUS

* pyTNC._on_receive notes
    # interface = ax25int above
    # frame = the incoming UI frame (aioax25.frame.AX25UnnumberedInformationFrame)
    # match = Regular expression Match object, if regular expressions were used in
    #         the bind() call.
    #p ('_on_receive')
    #p (frame.header)
    #p (frame.header.destination)
    #p (frame.header.source)
    #p (frame.header.repeaters)
    #p (frame.header.cr)     # cd = Command Response bit
    #p (frame.header.src_cr)
    #p ('Control %x' %(frame.control))
    #p (frame.pid)
    #p (frame.frame_payload)
    #p (frame)
    #p (str(type(frame)))
    #p (type(frame) is aioax25.frame.AX25UnnumberedInformationFrame)
    #https://stackoverflow.com/questions/70181515/how-to-have-a-comfortable-e-g-gnu-readline-style-input-line-in-an-asyncio-tas

















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



    Command KISSDEV calls \/

    def kissDeviceTCP (self, device, host, port):
        self._kissDevices[device] = KissDevice (host, port, 'TCP')

        #self._kissDevices[dev].KissDevice = self.start_ax25_device (host, port, 'TCP')

    calls \/

     def start_ax25_device(self, host, port, phy):
            kissdevice = make_device(
            type="tcp", host="localhost", port=8001,
            log=self.logging, #.getLogger("ax25.kiss"),
            loop=self.loop
            )
            kissdevice.open() # happens in background asynchronously

            return kissdevice


    Command KISSINT calls \/

    def kissPort (self, interface):
            #axint = self.start_ax25_port (self._kissDevices[dev].KissDevice, kissPort)
            #self._kissDevices[dev].setKissPorts (kissPort, KissPort (axint, None, None, None))
            #self.start_ax25_station (dev, kissPort)

    Calls \/

    def start_ax25_port(self, port):
        ax25int = aioax25.interface.AX25Interface(
            kissport=kissdevice[int(kissPort)],         # 0 = HF; 2 = USB
            loop=self.loop, 
            log=self.logging, #.getLogger('ax25.interface')
        )

        ax25int.bind (self.on_rx, '(.*?)', ssid=None, regex=True)







Multi-Connects
The TNC makes it possible for you to talk to more than one person at the same time. Single port TNCs, such as the KPC-3 Plus, support 26 streams on the one port. Multi- port TNCs, such as the KPC-9612 Plus, support 26 streams per port.
The command MAXUSERS determines how many streams may be used at one time, per port, and the command USERS determines how many people can connect to the TNC per port. An incoming connect uses the next available stream. If the number of streams set by USERS is full, then a station attempting a connect with your TNC will receive a busy message instead of a connect. However, if MAXUSERS is set larger than USERS, you can still issue outgoing connects on additional streams.
To determine which port you are on, simply use the STATUS command, typing STAT at the command prompt. The TNC will report which streams are active and which one you are on. If you wish to remain on the current stream to communicate, no action is necessary. To change streams ( to make another connect or to send data to another
station already connected to you) type the STREAMSW character, the number of the port (if you are changing ports on a multi-port TNC), and the letter designation of the stream you wish to be on. No return or enter key is necessary.
For example, let’s assume you are using a KPC-9612 Plus and you are connected to WØXI on stream A of port 2 but you wish to return to a discussion with NØKN on stream B of port 1. Whether in command mode or convers mode, simply enter “|1b” and the TNC will switch to port 1, stream B. When you do this, the CON and STA lights on the front panel will switch with you, reporting the status of the new stream.
If you are connected and have MONITOR or MCON OFF, the normal headers containing the “to” and “from” callsigns will not be shown. The setting of STREAMEV will then determine how often you see the stream designator. This parameter comes defaulted OFF, so the stream designators are only shown when a change in streams occurs. Turning this command ON will make the stream designators show on every connected packet received. Turning STREAMCA ON will also add the callsign of the “from” station beside the stream designator.

***
Connect requests may only be initiated in the Command Mode and the connect will be established on the current stream.



CONOK {ON | OFF}
default ON Multi-Port
When ON, connect requests from other TNCs will be automatically acknowledged and a <UA> packet will be sent. The standard connect message, with stream ID if appropriate, will be output to the terminal and the mode specified by CONMODE will be entered on the I/O stream if you are not connected to another station and NOMODE is OFF.
When OFF, connect requests from other TNCs will not be acknowledged and a <DM> packet will be sent to the requesting station. The message “connect request: (callsign of whoever is trying to connect to you)” will be output to your terminal if INTFACE is TERMINAL or NEWUSER.
When CONOK is OFF, you can still connect to your mailbox.
When operating with multiple connects allowed, the connection will take place on the next available stream. Connect requests in excess of the number allowed by the USERS command will receive a <DM> response and the “connect request: (call)” message will be output to your terminal if INTFACE is TERMINAL or NEWUSER.
See also: conmode, connect, intface, maxusers, monitor, nomode, and users


