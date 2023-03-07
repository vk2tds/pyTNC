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


import string



def is_hex(s):
     hex_digits = set(string.hexdigits)
     # if s is long, then it is faster to check against a set
     return all(c in hex_digits for c in s)


def to_user (command, old, new):
    if old is None:
        if new is True:
            new = 'On'
        if new is False:
            new = 'Off'
        return ('%s%s' % (command.ljust(13), str(new).ljust(10)))
    else:
        # old is NOT None
        if new is True:
            new = 'On'
        if new is False:
            new = 'Off'
        if old is True:
            old = 'On'
        if old is False:
            old = 'Off'
        return ('%s was %s' % (command, old))