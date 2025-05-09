
**Automotive Timings**
The ignition sense feature can be used to turn the Karbon unit on and off with a battery, 
the vehicle's ignition (given proper electrical setup), or the use of a switch. Automotive timings and ignition sense can 
be toggled by bridging DC power to the IGN pin, see the diagram below. The proper sequence microcontroller settings must 
be set before using either the BIOS settings, LPMCU tool, or this Python API. 

The unit will turn on when power is applied to the IGN pin, and turn off when power is removed.

Ignition sensing can be enabled and adjusted through a UART connection to the system's microcontroller. 
This program additionally administers the LPMCU communication protocol to the sequence microcontroller to allow .

**Terminal Block Diagram of K-52x - Ignition pin is on leftmost side**

.. code-block:: text

    ---------------------------------
    ||  _     _     _     _     _  ||
    || |_|   |_|   |_|   |_|   |_| ||  
    || IGN |  +  |  +  |  -  |  -  ||  
    ---------------------------------

**Terminal Block Diagram of HX-52x**

.. code-block:: text

    ---------------------------
    ||  _     _     _     _  ||
    || |_|   |_|   |_|   |_| || 
    ||  -  |  +  |  +  |  -  ||
    ---------------------------

Note: The HX-52x does not have and ignition pin. So Automotive mode is not supported.

**Command Summary**

+---------------------------------+-------------------------------+----------------------------+--------------------+
| Command                         | Description                   | Parameters                 | Returns            |
+=================================+===============================+============================+====================+
| ``get_automotive_mode``         | Get the automotive mode of    | None                       | (0:low, 1:high)    |
|                                 | the device. Enables or        |                            |                    |
|                                 | disables system automotive    |                            |                    |
|                                 | features.                     |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_automotive_mode``         | Set the automotive mode of    | (0:low, 1:high)            | Status             |
|                                 | the device. Enables or        |                            |                    |
|                                 | disables system automotive    |                            |                    |
|                                 | features.                     |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_low_power_enable``        | Get the low power enable      | None                       | (0:low, 1:high)    |
|                                 | status from the MCU. Enables  |                            |                    |
|                                 | entering a very low power     |                            |                    |
|                                 | state when the system powers  |                            |                    |
|                                 | off.                          |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_low_power_enable``        | Set the low power enable      | (0:low, 1:high)            | Status             |
|                                 | status in the MCU. Enables    |                            |                    |
|                                 | entering a very low power     |                            |                    |
|                                 | state when the system powers  |                            |                    |
|                                 | off.                          |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_start_up_timer``          | Get the start-up timer        | None                       | Integer: Start-up  |
|                                 | value from the MCU. Controls  |                            | timer value in     |
|                                 | the number of seconds the     |                            | seconds.           |
|                                 | ignition input must be stable |                            |                    |
|                                 | before powering on.           |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_start_up_timer``          | Set the start-up timer        | Integer: Start-up timer    | Status             |
|                                 | value in the MCU. Controls    | value in seconds.          |                    |
|                                 | the number of seconds the     |                            |                    |
|                                 | ignition input must be stable |                            |                    |
|                                 | before powering on.           |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_soft_off_timer``          | Get the soft-off timer        | None                       | Integer: Soft-off  |
|                                 | value from the MCU. Controls  |                            | timer value in     |
|                                 | the number of seconds the     |                            | seconds.           |
|                                 | ignition input can be low     |                            |                    |
|                                 | before the MCU requests a     |                            |                    |
|                                 | power-down event.             |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_soft_off_timer``          | Set the soft-off timer        | Integer: Soft-off timer    | Status             |
|                                 | value in the MCU. Controls    | value in seconds.          |                    |
|                                 | the number of seconds the     |                            |                    |
|                                 | ignition input can be low     |                            |                    |
|                                 | before the MCU requests a     |                            |                    |
|                                 | power-down event.             |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_hard_off_timer``          | Get the hard-off timer        | None                       | Integer: Hard-off  |
|                                 | value from the MCU. Controls  |                            | timer value in     |
|                                 | the number of seconds the     |                            | seconds.           |
|                                 | ignition input can be low     |                            |                    |
|                                 | before the MCU forces the     |                            |                    |
|                                 | system to power down.         |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_hard_off_timer``          | Set the hard-off timer        | Integer: Hard-off timer    | Status             |
|                                 | value in the MCU. Controls    | value in seconds.          |                    |
|                                 | the number of seconds the     |                            |                    |
|                                 | ignition input can be low     |                            |                    |
|                                 | before the MCU forces the     |                            |                    |
|                                 | system to power down.         |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_shutdown_voltage``        | Get the shutdown voltage      | None                       | Integer: Shutdown  |
|                                 | value from the MCU. The       |                            | voltage in         |
|                                 | threshold voltage for         |                            | millivolts.        |
|                                 | triggering low-voltage        |                            |                    |
|                                 | shutdown events.              |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_shutdown_voltage``        | Set the shutdown voltage      | Integer: Shutdown voltage  | Status             |
|                                 | value in the MCU. The         | in millivolts.             |                    |
|                                 | threshold voltage for         |                            |                    |
|                                 | triggering low-voltage        |                            |                    |
|                                 | shutdown events.              |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``get_all_automotive_settings`` | Get all automotive settings   | None                       | Dictionary:        |
|                                 | from the MCU. Returns a       |                            | All automotive     |
|                                 | dictionary containing all     |                            | settings.          |
|                                 | automotive configurations.    |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+
| ``set_all_automotive_settings`` | Set all automotive settings   | List: [amd, lpe, sut, sot, | List: Status code  |
|                                 | in the MCU. Takes a list of   | hot, sdv]                  | of each command.   |
|                                 | values for all settings.      |                            |                    |
+---------------------------------+-------------------------------+----------------------------+--------------------+