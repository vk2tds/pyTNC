#!/usr/local/python3

# This code was developed for MacOS but should work under Windows and Linux

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public 
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, 
# see <https://www.gnu.org/licenses/>.

# Having said that, it would be great to know if this software gets used. If you want, buy me a coffee, or send me some hardware
# Darryl Smith, VK2TDS. darryl@radio-active.net.au Copyright 2023






class Monitor:
    def __init__ (self):
        self._completer = None
        self._output = None
        self._tnc = None

    @property
    def completer (self):
        return self._completer
    
    @completer.setter
    def completer (self, c):
        self._completer = c

    def setOutput (self, o):
        self._output = o

    def setTnc (self, t):
        self._tnc = t

    def _on_receive_trace (self, textInterface, frame): 
        bytes = frame.__bytes__() 
        paclen = len(bytes)
        if self._completer.options['STREAMSHOW'].Value:
            self.output (textInterface + ' ->')
        self.output (    'byte  ------------hex display------------ -shifted ASCII-- -----ASCII------')
        offset = 0

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
            self.output (line)



    def _on_receive_monitor (self, interface, frame):


        port = interface._port
        device = 'Unknown'

        if type(port._device) == aioax25.kiss.TCPKISSDevice:
            for d in self._tnc.kiss_interface.kissDevices:
                kD = self._tnc.kiss_interface.kissDevices[d]
                if kD._conn_args['host'] == port._device._conn_args['host'] and kD._conn_args['port'] == port._device._conn_args['port']:
                    device = d

        textInterface = device + ':' + str(port._port)


        calls = re.split (r"[*>,]", str(frame.header))
        calls = [value for value in calls if value != '']
        lcalls = self._completer.options['LCALLS'].Value.split(',') if not self._completer.options['LCALLS'].Value is None else []
        budlist = self._completer.options['BUDLIST'].Value
        mall = self._completer.options['MALL'].Value
        mcon = self._completer.options['MCON'].Value
        mrpt = self._completer.options['MRPT'].Value
        streamshow = self._completer.options['STREAMSHOW'].Value
        headerln = self._completer.options['HEADERLN'].Value
        adrdisp = self._completer.options['ADRDISP'].Value
        trace = self._completer.options['TRACE'].Value
        mtrans = self._completer.options['MTRANS'].Value


        if self._tnc.mode == self._tnc.modeTransparent:
            if mtrans == False:
                # No Monitoring
                return False

        displayPacket = False

        #TODO _tnc.connected is ARGH!!!
        if self._tnc.connected:
            if mcon == False:
                # do not display in Connected mode if mcon = False
                return

        if set(calls).intersection(lcalls):
            if budlist == True:
                # Monitor these
                True
            else:
                # Ignore these
                return
        else:
            if budlist == True:
                # Ignore these
                return
            else:
                # Monitor these
                True

        if mall:
            # mon connected and unconnected
            True
        else:
            # mon unconnected only
            if type(frame) is aioax25.frame.AX25UnnumberedInformationFrame:
                True
            else:
                return

        if self._completer.options['MONITOR'].Value: # MONITOR ON
            True
        else:
            # If Monitor is OFF, Return
            return
            
        #MRPT On: WB9FLW>AD7I,K9NG*,N2WX-7:Hi Paul.
        #MRPT OFF: WB9FLW>AD7I:Hi Paul.
        if mrpt:
            callsigns = frame.header.source.__str__() + '>' + frame.header.destination.__str__() + ',' + frame.header.repeaters.__str__()
        else:
            callsigns = frame.header.source.__str__() + '>' + frame.header.destination.__str__()

        #if type(frame) is aioax25.frame.AX25RawFrame:
        #    self.output ('--->AX25RawFrame')
        #    self.output ('RAW' + str(frame))

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

        #ADRdisp - default ON - N4UQQ>N4UQR,TPA5* <UI R>:This is a monitored frame.
        if hasattr(frame, 'payload'):
            payload = str(frame.payload.decode())
        else:
            payload = '<NO_PAYLOAD>'

        out = ''
        if headerln:
            #HEADERLN On: KV7D>N2WX: Go ahead and transfer the file.
            if adrdisp:
                out = callsigns + control
            else:
                out = payload 
        else:
            #HEADERLN Off: N2WX>KV7D:
            #           Sorry, I'm not quite ready yet.
            if adrdisp:
                out = callsigns + control + payload
            else:
                out = payload

        if streamshow: 
            out = textInterface + ' | ' + out


        self.output (out)

        if trace:
            # Trace mode enabled.
            self._on_receive_trace (textInterface, frame)

    def output(self, line):
        self._output (line)



