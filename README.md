===============
OnLogicNuvoton Module
===============

The OnLogic Nuvoton Mmdule Provides a set of tools to interface with peripherals on Onlogic K/HX-52x series computers.

On the K52x it can send commands to the DIO Add in card and the Sequence Micro to control automotive timings.
On the HX52x it can send commands to the DIO Add in card.

--------------
Setup Required
--------------

You will need to install Python3 prior to following this guide.

# Setting up OnLogicNuvotonManager on Windows


# Setting up OnLogicNuvotonManager in a Python3 venv on Ubuntu 24.04 LTS 
Linux Ubuntu has enforced a stricter package management scheme in the new 24.04 LTS distribution to avoid interfering with global package dependencies used by the OS. While this is a more stable way to administer Python on a system, it is also more complex to program in user environments. To run the package OnLogicNuvotonManager in Ubuntu, it's best practice to use a venv.

* Creating a venv: 	$ python3 -m venv <path/to/venv> 
    * (One can get <path/to/venv> by navigating to desired directory in terminal and inputting pwd)
* Activating a venv: 	$ source <path/to/venv>/bin/activate
* Deactivating a venv: 	$ deactivate

- When the venv is activated, running any python scripts will use the venv's interpreter and packages. But, when running a script that needs root privileges (sudo python ...), the venv's Python won't be used, even if its activated. My solution has been to explicitly use the venv's interpreter when running a Python script. 

$ sudo <path/to/venv>/bin/python somescript.py

We have to use whole path because we need to sudo in, and we can't access IO without sudo privaleges 

After, set up required packages in venv
* pip install -e .
* Double Check With: 'pip freeze' within local directory

------------------------
Shell Transport Protocol
------------------------

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

This Python Module administers this protocol in communication with both DIO and Sequence microcontrollers.
It makes native Python datatypes, converts them to byte compatable communication, and administers this process
with additional type and value checking.  

**Note** the CPU uses two distinct communication protocols to talk with the DIO and Sequence Microcontrollers.
1. CDC-USB with the DIO Card
2. UART with the Sequence Micro

For this reason, the user must manually specify the serial port name for the sequence micro .claim() method in the AutomotiveManager class, whereas for the DioHandler, the .claim() method can be left blank and the program will autolock on the serial connection label. 