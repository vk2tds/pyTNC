# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in
progress, with lots more work needed. Thing such as error checking are rarely implemented. 

The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added
to allow settings to be stored for use at runtime. 

* Type 'HELP ALL' for information on all the commands. This needs to be longer.
* Exiting CONV mode is an issue at the moment. ALT-C on my Mac exits into command mode
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









KISSDEV
KISSINT
PORT
STREAM




new command STREAMSHOW - show the name of the interface when showing packets













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



