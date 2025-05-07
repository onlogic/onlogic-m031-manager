# Use of a Python venv in Ubuntu 24.04 LTS 

Linux Ubuntu has enforced a stricter package management scheme in the new 24.04 LTS distribution to avoid interfering with global package dependencies used by the OS. While this is a more stable way to administer Python on a system, it is also more complex to program in user environments. To run the package OnLogicNuvotonManager in Ubuntu, it's best practice to use a venv.

* Creating a venv: 	$ python3 -m venv <path/to/venv> 
    * (One can get <path/to/venv> by navigating to desired directory in terminal and inputting pwd)
* Activating a venv: 	$ source <path/to/venv>/bin/activate
* Deactivating a venv: 	$ deactivate

- When the venv is activated, running any python scripts will use the venv's interpreter and packages. But, when running a script that needs root privileges (sudo python ...), the venv's Python won't be used, even if its activated. My solution has been to explicitly use the venv's interpreter when running a Python script. 

$ sudo <path/to/venv>/bin/python somescript.py

We have to use whole path because we need to sudo in, and we can't access IO without sudo privaleges 

# Set up required packages in venv
* pip install -e .
* Double Check With: 'pip freeze' within local directory

# Shell Transport Protocol
-----------------------

A protocol is used for transferring commands.  By convention, the CPU
issues commands, and the MCU listens and responds to them.  Each valid command
message generates a response message.

Each message consists of a 4-byte header: a fixed 0x01 start
byte, the CRC-8 of the message, the length of any data following the header,
and the kind of message.  The CRC-8 is calculated from the third byte of the
message (the length byte) onward, and uses the SMBUS polynomial (0x107).

A primitive form of flow control is built into the protocol.  After a byte is
received, the receiver processes it and replies with `\r` if the byte was
expected, or `\a` if not.  An example command/response sequence might look like
this:

```
CPU                                          MCU
(start of frame) 0x01 ->
                        <- (acknowledge)      \r
(crc-8)          0x38 ->
                        <- (acknowledge)      \r
(data length)    0x00 ->
                        <- (acknowledge)      \r
(message kind)   0x08 ->
                        <- (acknowledge)      \r
<MCU processes command>
                        <- (start of frame) 0x01
(acknowledge)    \r   ->
                        <- (crc-8)          0xc4
(acknowledge)    \r   ->
                        <- (data length)    0x01
(acknowledge)    \r   ->
                        <- (message kind)   0x08
(acknowledge)    \r   ->
                        <- (data byte)      0x01
(acknowledge)    \r   ->
```

This sequence shows the CPU sending a `kGet_LowPowerEnable` message with no
additional data and the MCU responding with a `kGet_LowPowerEnable` response
with one byte of additional data.