# pyTNC
AX.25 Ham Radio TNC

This code is designed to implement a TAPR TNC-2 type interface, written in Python. The code is definitely a work in
progress, with lots more work needed. Thing such as error checking are rarely implemented. 

The software is designed to conenct to a KISS TNC via TCP. The best solution for this might be DIREWOLF. Commands have been added
to allow settings to be stored for use at runtime. 

* Type 'HELP ALL' for information on all the commands. This needs to be longer.
* Exiting CONV mode is an issue at the moment. ALT-C on my Mac exits into command mode
* You can connect to Eliza by typing 'C ELIZA' at the CMD prompt. Exit by typing 'BYE'

