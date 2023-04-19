BUGS


* Timezone is stored when the specific information is saved. If you cange to or from UTC, dates and times will be in whatever 
format they were in until refreshed
* If TAB completion is NOT working, GNU Readline may not be working. It may not be needed, depending on the system
* cannot work out an escape command in readline in CONV mode. Hacked by doing Alt-C which sends ç
* Redline - https://pypi.org/project/gnureadline/
* split callsign storage from conect.kiss_interface() such that you can have a dedicated call per interface

* At the “cmd:” prompt, type |2a and press the enter key. This would move to port 2 on stream A

* Need to queue printing of return values from processing and display before the command prompt
* semaphores really should be based on asyncio.


Future 
* Libedit readline
    if 'libedit' in readline.__doc__:
        print("Found libedit readline")
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        print("Found gnu readline")
        readline.parse_and_bind("tab: complete")


Need to implement CONOK




* This code is not intended to deal with teletype machines or the like. If your display device works with Python, it shoudl work here. 



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






#Right, so the `Signal()` class is from the `signalslot` package.  It
#has a `.connect()` method to which you pass a function reference which
#takes keyword arguments.  It takes some ideas from Qt which uses this
#"observer" pattern quite heavily.
#
#https://signalslot.readthedocs.io/en/latest/
#
#So in this case; we need a handler that picks up the `peer` argument,
#something like:
#
#```
#def _on_connection_rq(peer, **kwargs):
#   # Accept the connection
#   peer.accept()
#   # do something else with peer here
#
#station.connection_request.connect(_on_connection_rq)



* I have disconnected ELIZA at the moment. She *MIGHT* be connected back in the future. 
