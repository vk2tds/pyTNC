# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in progress, with lots more work needed. Thing such as error checking are rarely implemented. The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added to allow settings to be stored for use at runtime. 

This software mostly implements 'Connected Mode' functions. Unconnected Information (UI) modes such as APRS are better implemented in other software, such as in Direwolf itself. This softwaer was written because there really was not anything out there for the Mac dealing with Connected Mode

It relies on a number of libraries that might not be installed by default under Python. See the INSTALLING section below. These include:
* aioax25
* asyncio
* gnureadline
* tabulate
* tracback

The software has a command line GUI. At some point, a TCP interface would be cool, so that you could telnet in remotely. We are not to that point yet. The  commands are basically TNC-2, with changes. They should all be documented if you type 'HELP ALL'. You can also get help with a command by replacing 'ALL' with the name of the command. For instance 'HELP CONNECT' will tell you how to connect. This help does need to be expanded. If gnureadline or readline is opperating correctly, tab completion *should* work. No promises though.

At the time of writing, another TNC can connect *TO* pyTNC successfully. The reverse path connecting *FROM* pyTNC does not work yet. I have not yet tested DIGIPEATING, and I have no idea if it will work or not. Streams have been implemented, but more work is needed on them. Per KISS port or per STREAM settings are on my agenda. 

Some commands may be implemented in the GUI only, where values change, but nothing happens in the background. This software is still under development, and might always be. Also, some commands might only work the first time they are run. KISSINT and KISSDEV are functions that likely work this way, when they are run with options modifying existing values. 

There are custom settings are stored in the same directory as the code. These are user settings and  work exactly as if they had been typed on the pyTNC command line. The file is called 'custom.txt'. 

#TODO: only open the standard 'custom.txt' if a local copy does not exist.

== TNC Operational Modes ==

There are three TNC operational modes, just like most TNC's. They are:
* Command Mode
* Converse Mode
* Transparent Mode

Command Mode is, as you would expect, how you interface with the TNC settings. Converse and Transparent modes conversely deal with communications with a remote station. 

One of the best ways to become familiar with Command Mode is to start the software, whereupon you will be presented with Command Mode. From there typing the command 'HELP ALL' will give you a list of all the possible commands that pyTNC knows about. If you ever just need help on a single command, you can type 'HELP' followed by the name of the command. Thus, typing 'HELP CONNECT' will display the help on the 'CONNECT' command.

Tab Completion *should* be operational in Command Mode. If it does not, this would be an issue with 'readline' or 'gnureadline'. The 'gnureadline' library works well for me under MacOS. 

From Command Mode you can enter Converse and Transparent Mode by typing 'CONV' (or 'CONVERSE') to get into Converse mode; and 'TRANS' to get into Transparent mode. Once in Converse or Transparent Mode, anything you type will be sent to the station you are connected to and vice versa. 

Exiting back to Command Mode is a minor issue at the moment. ALT-C on my Mac exits into Command Mode. In the future, Ctrl-C will need to be implemented. 

== Changing the Callsign ==

To set the callsign, use a command like 'MYCALL VK2TDS-10', replacing my callsign with your callsign obviously. The callsign should be set before you use the KISS commands below. In future this will likely be fixed. It might even already be fixed. 

== Connecting to a TNC == 

At the moment, the software is required to connect to a KISS TNC via TCP. More connection modes will come. Since I am using a Mac, this is what I need to use. There are two very important KISS commands that need to be used, KISSDEV and KISSINT. KISSDEV should be used first, since it sets up the device, followed by KISSINT, which sets up the interface on that device. 

An example appears below:

* KISSdev picopacket tcp localhost 8001
* KISSInt picopacket 0

Looking at the KISSDEV line, the first thing to note is the name 'picopacket'. This is freeform text. The only requirement is that it is the same as the ones used in KISSINT.

We then go to TCP, indicating that we are connecting via TCP. Then onto the hostname and port for the KISS interface. This is fairly straightforward. At the moment, TCP and SERIAL transports have been implemented. 

Each KISS device can have miltiple interfaces. An interface is generally a radio port. These start at index 0, and go up from there. 

The KISSINT command basically just says which KISS interfaces to activate. 

You can see what has been set up by just typing the commands 'KISSINT' and 'KISSDEV'. However, a better way is using the 'PORT' command.

There needs to be a default interface for us to use. To make things easy, we use the 'PORT' command to see the available ports and select a new one. A port might be called something like 'picopacket:0'. To change to that port, type 'PORT picopacket:0'. If there is an asterisk next to one of the ports, that means it is the currently selected port. You can ignore the asterisk if changing ports.


The TNC can operate in AX.25v2.0 or AX.25v2.2 mode. In the latter, the protocol will fall back to AX.25v2.0 if the other end does not support the more modern version. You can force the TNC to use AX.25v2.0 with teh command 'AXVERSION AX25_20'.

== Streams ==

At the time of writing, streams are still being developed. The idea first is that a Stream is 'attached' to a KISSport. You can then make or receieve connections on that KISSport. Multiple streams can be 'attached' to the same KISSport, so that you could have multiple connections active at the same time on the one KISSport. For example, you could connect to VK2SE on Stream A, and VK2AAB on Stream B. Any packets that come in on Stream A whilst you are active on Stream B would be cached until you change stream. PORTS and Connections operate within a stream. Connections stay in their current state when you change streams. When you return to a stream, it is as if you had never left it. 

You can see the current stream by typing 'STREAM' and change streams with the stream command followed by a character, for instance, 'STREAM B'. 

The 'PORT' command will show the KISSport for all streams, with an asterisk for the KISSport that this Stream is currently connected to. You can change the port the stream is connected to with a command such as 'PORT picopacket:0' .

There is a new command called 'STREAMSHOW', which when active, will display the stream when monitoring packets. Beware, this command may be changed to 'PORTSHOW' as the concept of streams is further developed. 






#https://pynput.readthedocs.io/en/latest/keyboard.html ????????
#http://pymotw.com/2/readline/ ??????



# TNC2 Commands
# https://web.tapr.org/meetings/CNC_1986/CNC1986-TNC-2Setting-W2VY.pdf





TODO: have the custom.txt search in the home directory for the user too
TODO: Take over Control-C
TODO: Changing callsign after KISS is opened.
TODO: KISSDEV name case insenstive 
TODO: should it be STREAMSHOW or PORTSHOW??



=== ROM.PY ===
All the TNC commands, default values, help and more are stored in ROM.py. This file is processed by being read into a class. Certain values are then over-ridden by the custom.txt file entries. 





- `station`: `AX25Station` instance receiving the traffic
- `peer`: `AX25Peer` from whom the traffic was received from
- `frame`: The `AX25InformationFrame` containing the payload
- `data`: The receive buffer content (`bytes`), which can be empty





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



