====================
OnLogicNuvotonManager
====================

The OnLogicNuvotonManager provides a set of tools to interface with peripherals on Onlogic K/HX-52x series computers.


On the HX52x, it can send commands to the DIO add-in-card.
On the K52x, it can send commands both to the DIO add-in-card and the sequence microcontroller to control automotive timings.


Setup Required
==============

You will need to install Python 3 prior to following this guide. You can download Python from python.org. Ensure Python and pip are added to your system's PATH during installation.

Setting up OnLogicNuvotonManager on Windows (Native Install)
-------------------------------------------------------------

These steps guide you through installing the OnLogicNuvotonManager directly into your system's Python environment.

1. Install Python 3:
   If you haven't already, download and install Python 3 from python.org.
   Make sure to check the box that says "Add Python to PATH" during the installation.

2. Open Command Prompt or PowerShell:
   You can search for "cmd" or "powershell" in the Start Menu.

3. Navigate to the Project Directory:
   Use the ``cd`` command to change to the directory where you have the OnLogicNuvotonManager files (e.g., where the ``setup.py`` file is located).
   Example::

     cd path\\to\\OnLogicNuvotonManager

4. Install Required Packages:
   Run the following command to install the package. This will install it into your global Python site-packages or user-specific site-packages.::

     pip install -e .

5. Verify Installation:
   To see all installed Python packages in your environment (this will include packages beyond this project)::

     pip freeze

6. Running Scripts Requiring Elevated Privileges:
   For operations that require direct hardware access (like interacting with serial ports), you might need to run your Python scripts 
   from a Command Prompt or PowerShell that has been opened "As Administrator". To do this, right-click on the Command Prompt/PowerShell 
   icon and select "Run as administrator".

Setting up OnLogicNuvotonManager in a Python3 venv on Ubuntu 24.04 LTS
-----------------------------------------------------------------------
Linux Ubuntu has enforced a stricter package management scheme in the new 24.04 LTS distribution to avoid interfering with global package dependencies used by the OS. While this is a more stable way to administer Python on a system, it is also more complex to program in user environments. To run the package OnLogicNuvotonManager in Ubuntu, it's best practice to use a venv.

* Creating a venv::

    $ python3 -m venv <path/to/venv>
    (One can get <path/to/venv> by navigating to desired directory in terminal and inputting ``pwd``,
    
    .. code-block:: bash

      python3 -m venv venv

    will likely work as well
    )

* Activating a venv::

    .. code-block:: bash

      $ source <path/to/venv>/bin/activate

* Deactivating a venv::

    .. code-block:: bash

    $ deactivate

- When the venv is activated, running any python scripts will use the venv's interpreter and packages. But, when running a script that needs root privileges (``sudo python ...``), the venv's Python won't be used, even if its activated. My solution has been to explicitly use the venv's interpreter when running a Python script.::

  .. code-block:: bash

  $ sudo <path/to/venv>/bin/python somescript.py

  We have to use whole path because we need to sudo in, and we can't access IO without sudo privaleges

After, set up required packages in venv:
* ``pip install -e .``
* Verify with: ``pip freeze`` within local directory

Examples
========
There are several examples in the ``examples`` directory. The examples
are designed to run from the command line and follow the setup seen above.
Make sure, however, that for Automotive settings, you enable the COM visibility in
the BIOS. This is done by ...

Shell Transport Protocol
========================

A protocol is used for transferring commands. By convention, the CPU
issues commands, and the MCU listens and responds to them. Each valid command
message generates a response message.

Each message consists of a 4-byte header: a fixed ``0x01`` start
byte, the CRC-8 of the message, the length of any data following the header,
and the kind of message. The CRC-8 is calculated from the third byte of the
message (the length byte) onward, and uses the SMBUS polynomial (``0x107``).

A primitive form of flow control is built into the protocol. After a byte is
received, the receiver processes it and replies with ``\\r`` if the byte was
expected, or ``\\a`` if not. An example command/response sequence might look like
this:

.. code-block:: text

  CPU                                          MCU
  (start of frame) 0x01 ->
                          <- (acknowledge)      \\r
  (crc-8)          0x38 ->
                          <- (acknowledge)      \\r
  (data length)    0x00 ->
                          <- (acknowledge)      \\r
  (message kind)   0x08 ->
                          <- (acknowledge)      \\r
  <MCU processes command>
                          <- (start of frame) 0x01
  (acknowledge)    \\r   ->
                          <- (crc-8)          0xc4
  (acknowledge)    \\r   ->
                          <- (data length)    0x01
  (acknowledge)    \\r   ->
                          <- (message kind)   0x08
  (acknowledge)    \\r   ->
                          <- (data byte)      0x01
  (acknowledge)    \\r   ->

This sequence shows the CPU sending a ``kGet_LowPowerEnable`` message with no
additional data and the MCU responding with a ``kGet_LowPowerEnable`` response
with one byte of additional data.

This Python Module administers this protocol in communication with both DIO and Sequence microcontrollers.
It makes native Python datatypes, converts them to byte compatable communication, and administers this process
with additional type and value checking.

**Note** the CPU uses two distinct communication protocols to talk with the DIO and Sequence Microcontrollers.
1. CDC-USB with the DIO Card
2. UART with the Sequence Micro

For this reason, the user must manually specify the serial port name for the sequence micro ``.claim()`` method in the ``AutomotiveManager`` class, 
whereas for the ``DioHandler``, the ``.claim()`` method can be left blank and the program will autolock on the serial connection label.

Status Types:
------------

The status types are defined in src/command_set.py and are used to mark and indicate failures during 
different stages of the LPMCU protocol, including command construction, sending, 

The table below is a summary of the status types, but note that method class members
do not all report the status types in the same way. 

+----------------------------------------------+-------+---------------------------------------------------+
| Status Type                                  | Value | Description                                       |
+==============================================+=======+===================================================+
| `SUCCESS`                                    |   0   | The LPMCU protocol completed successfully.        |
+----------------------------------------------+-------+---------------------------------------------------+
| `SEND_CMD_FAILURE`                           |  -1   | Failed to send the command during the initial     |
|                                              |       | transmission process.                             |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_UNEXPECTED_PAYLOAD_ERROR`              |  -2   | The received payload did not match the expected   |
|                                              |       | format or structure during validation.            |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_CRC_ERROR`                       |  -3   | The CRC value of the received frame did not       |
|                                              |       | match the expected value, indicating corruption.  |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_ACK_ERROR`                       |  -4   | The acknowledgment frame validation failed,       |
|                                              |       | indicating an issue with the tail frame.          |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_SOF_ERROR`                       |  -5   | The start-of-frame (SOF) byte `0x01` was not      |
|                                              |       | found in the received frame.                      |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_PARTIAL_FRAME_VALIDATION_ERROR`        |  -6   | Validation of a partially received frame failed,  |
|                                              |       | indicating incomplete or corrupted data.          |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_VALUE_ERROR`                     |  -7   | The received payload contained unexpected or      |
|                                              |       | invalid values.                                   |
+----------------------------------------------+-------+---------------------------------------------------+
| `FORMAT_NONE_ERROR`                          |  -8   | A `None` value was encountered during type        |
|                                              |       | formatting, indicating a missing or invalid type. |
+----------------------------------------------+-------+---------------------------------------------------+