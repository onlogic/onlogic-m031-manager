================================
OnLogicM031Manager Overview
================================

The OnLogicM031Manager provides a set of tools to interface with peripherals on Onlogic K/HX-52x series computers.

* On the HX-52x, it can send commands to the DIO add-in-card.
* On the K-52x, it can send commands both to the DIO add-in-card and the sequence microcontroller to control automotive timings.

Setup Required
--------------

Python3 must be installed prior to following this guide. Python3 can be installed from python.org. Ensure Python and pip are added to the system's PATH during installation.

Setting up OnLogicM031Manager on Windows (Native Install)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These steps serve as a guide for installing the OnLogicM031Manager directly into the local Windows Python environment.

1. Open Command Prompt or PowerShell:
   "cmd" or "powershell" are shorthands that can be entered in the Start Menu to pull them up.

2. Clone Project and Navigate to the Project Directory:
   In the parent directory where the project is to be run, run the following command in powershell to clone the repository

   .. code-block:: shell

      git clone git@github.com:onlogic/onlogic-m031-manager.git

   Or download the directory by clicking the green button and then ``Download ZIP`` on the top right of the GitHub page.

   Use the ``cd`` command to change to the directory where the OnLogicM031Manager files are located (same directory as where the ``setup.py`` file is located):

   .. code-block:: shell

      cd path\to\onlogic-m031-manager

3. Install Required Packages:
   Run the following command to install the package. This will install it into the global Python site-packages or user-specific site-packages::

     pip install -e .

5. Verify Installation:
   To see all installed Python packages in the global environment (this will include packages beyond this project)::

     pip freeze

6. Running Scripts Requiring Elevated Privileges:
   For operations that require direct hardware access (like interacting with serial ports), the Python scripts may need to be run 
   from a Command Prompt or PowerShell that has been opened "As Administrator". To do this, right-click on the Command Prompt/PowerShell 
   icon and select "Run as administrator".

Setting up OnLogicM031Manager in a Python3 venv on Ubuntu 24.04 LTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Linux Ubuntu has enforced a stricter package management scheme in the new 24.04 LTS distribution to avoid interfering with global package dependencies used by the OS. 
While this is a more stable way to administer Python on a system, it is also more complex to program in user environments. 
To run the OnLogicM031Manager package in Ubuntu, it's best practice to use a venv. Download the OnLogicM031Manager package by following step 2 above.

* Creating a venv:

  .. code-block:: shell

    $ python3 -m venv <path/to/venv>

  One can get <path/to/venv> by navigating to desired directory in terminal and inputting ``pwd``,

  .. code-block:: shell

      python3 -m venv venv

  Will likely work as well

* Activating a venv::

      $ source <path/to/venv>/bin/activate

* Deactivating a venv::

    $ deactivate

* When the venv is activated, running any python scripts will use the venv's interpreter and packages. 
  But, when running a script that needs root privileges (``sudo python ...``), the venv's Python won't be used, even if it's activated. 
  One solution is to explicitly use the venv's interpreter when running a Python script::

  $ sudo <path/to/venv>/bin/python somescript.py

* The whole path must be used to sudo in, and IO cannot be accessed without sudo privaleges

After, set up required packages in venv:

* ``pip install -e .``
* Verify with: ``pip freeze`` within local directory

Examples
========
There are several examples in the ``examples`` directory. The examples
are designed to run from the command line and follow the setup seen above.
Make sure, however, that for Automotive settings, COM visibility is enabled within
the BIOS.

The examples are designed to be run from the command line with:

.. code-block:: shell

  sudo <path/to/venv>/bin/python3 dio_implementation.py

for the dio_implementation.py script in Ubuntu, for example.

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
received, the receiver processes it and replies with ``\r`` if the byte was
expected, or ``\a`` if not. An example command/response sequence might look like
this:

.. code-block:: text

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
--------------

The status types are defined in src/command_set.py and are used to mark and indicate failures during 
different stages of the LPMCU protocol.

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
| `RECV_FRAME_NACK_ERROR`                      |  -3   | The acknowledgment frame validation failed,       |
|                                              |       | indicating an issue with the last index of frame. |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_CRC_ERROR`                       |  -4   | The CRC value of the received frame did not       |
|                                              |       | match the expected value, indicating corruption.  |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_ACK_ERROR`                       |  -5   | Mismatched ACKs in the send of frame. May         |
|                                              |       | indicate issues with MCU receiving cmds from CPU. |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_SOF_ERROR`                       |  -6   | The start-of-frame (SOF) byte `0x01` was not      |
|                                              |       | found in the received frame.                      |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_PARTIAL_FRAME_VALIDATION_ERROR`        |  -7   | Validation of a partially received frame failed,  |
|                                              |       | likely incomplete/corrupted data in mcu response. |
+----------------------------------------------+-------+---------------------------------------------------+
| `RECV_FRAME_VALUE_ERROR`                     |  -8   | The received payload contained unexpected or      |
|                                              |       | invalid values.                                   |
+----------------------------------------------+-------+---------------------------------------------------+
| `FORMAT_NONE_ERROR`                          |  -9   | A `None` value was encountered during type        |
|                                              |       | formatting, indicating a missing or invalid type. |
+----------------------------------------------+-------+---------------------------------------------------+
| `SHUTDOWN_VOLTAGE_OVER_SYSTEM_VAL`           |  -10  | System voltage not underneath low-voltage shut-   |
|                                              |       | down value + 0.2V.                                |
+----------------------------------------------+-------+---------------------------------------------------+