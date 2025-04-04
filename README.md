Note:

We need to verify that certain functions are being recieved and that the transport shell is sending back the correct values:
```
********************
[b'\x01', b'W', b'\x02', b' ', b'\x03', b'\x01', b'\x07']
get_di: Pin: 3 | Val: 1
********************
[b'\r', b'\r', b'\r', b'\r', b'\r', b'\r', b'\r']
ERROR | NON-BINARY DATATYPE DETECTED
set_do: Pin: 3 | Val: -1
********************
[b'\x01', b'\x86', b'\x02', b'"', b'\x03', b'\x00', b'\x07']
get_do: Pin: 3 | Val: 0
********************
[b'\r', b'\x07', b'\x07', b'\x07', b'\x07', b'\x07', b'\x07']
ERROR | NON-BINARY DATATYPE DETECTED
get_di_contact: Contact Type Val: -1
********************
[b'\r', b'\x07', b'\x07', b'\x07', b'\x07', b'\x07', b'\x07']
ERROR | NON-BINARY DATATYPE DETECTED
get_do_contact: Contact Type Val: -1
********************
[b'\x01', b'%', b'\x01', b'A', b'\x00', b'\x07', b'\x07']
[b'\x01', b'%', b'\x01', b'A', b'\x00', b'\x07', b'\x07']
ERROR | NON-BINARY DATATYPE DETECTED. return value: 7
set_di_contact: Contact Type Val: -1
********************
[b'\x01', b'\x1a', b'\x01', b'B', b'\x00', b'\x07', b'\x07']
ERROR | NON-BINARY DATATYPE DETECTED. return value: 7
set_do_contact: Contact Type Val: -1
Exiting...
```
get_do_contact

get_di_contact

set_do 

are responding irregularly - they seem to be formatted the same as the rest in transport layer, must be timing?
