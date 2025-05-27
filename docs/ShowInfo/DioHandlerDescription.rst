================================================
Digital Input/Output Module (DIO) Functionality
================================================

The DIO module can be configured in two modes: **wet contact** and **dry contact**. 
The outputs function as open drains. The inputs are high impedance. 

1. **DO Output Configurations:**

   **DO Wet Contact Mode (Suitable for Inductive Load Operation)**

   To function properly, the module **V+ should be connected to external power and ground**. The **high side of the load**
   should be connected to the **external power source**, and the **low side to the module DO pin**.

   * **Load current should not exceed 150 mA.**
   * **Voltage ranges should be 5 V to 30 V.**

   **Setup required for Output:**

   * 

   **DO Dry-Contact Mode**

   * Voltage is provided by the system. Each DO will output **11 V - 12.6 V when active**.

   **Setup required for Output:**

   * 

2. **Digital Input (DI) Configurations**

   **DI Wet Contact Mode**

   There is **no internal pull-up** to the DI[0:7] pins when set to WET mode.

   * Externally supplied **5 V - 30 V is recognized as logic 0**.
   * Externally supplied **0 V - 3 V is recognized as logic 1**.

   **Setup required for Input:**

   * 

   **DI Dry Contact Mode**

   When the contact type is set to DRY mode, DI[0:7] are **pulled up to the internal isolated ~12V supply**.

   * An **open/floating connection is recognized as logic 0**.
   * A **short to GND is recognized as logic 1**.

   **Setup required for Input:**

   * 

Operations are blocking but can be threaded to accomodate other processing operations, 
though the DIO card can only retrieve one value at a time over UART.

**Pinout**

.. code-block:: text

    ---------------------------------------------------------------
    ||  _     _     _     _     _     _     _     _     _     _  ||
    || |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Input
    || INT | DI7 | DI6 | DI5 | DI4 | DI3 | DI2 | DI1 | DI0 |  -  ||
    ---------------------------------------------------------------
    ||  _     _     _     _     _     _     _     _     _     _  ||
    || |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Output
    || GND | DO7 | DO6 | DO5 | DO4 | DO3 | DO2 | DO1 | DO0 |  +  ||
    ---------------------------------------------------------------

**Command Summary**

+--------------+-------------------------------+----------------------------------------+--------------------+
| Command      | Description                   | Parameters                             | Returns            |
+==============+===============================+========================================+====================+
| `get_di`     | Read digital input pin state  | pin val (0-7)                          | (0:low, 1:high)    |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `get_do`     | Read digital output pin state | pin val (0-7)                          | (0:low, 1:high)    |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `set_do`     | Set digital output pin state  | pin val (0-7) \| state (0:low, 1:high) | status             |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `set_all_do` | Set all DO pin states         | list of desired pin states             | status list        |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `get_all_do` | Read all DO pin states        |                                        | list of pin states |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `get_all_di` | Read all DI pin states        |                                        | list of pin states |
+--------------+-------------------------------+----------------------------------------+--------------------+
| `get_all_dio`| Read all DIO pin states       |                                        | list of pin states |
+--------------+-------------------------------+----------------------------------------+--------------------+

**Parameter Summary For Contact Modes**

+------------------+---------------------------------+---------------+---------------+
| Command          | Description                     | Parameters    | Returns       |
+==================+=================================+===============+===============+
| `set_di_contact` | Set digital input contact type  | (0:wet, 1:dry)|               |
+------------------+---------------------------------+---------------+---------------+
| `set_do_contact` | Set digital output contact type | (0:wet, 1:dry)|               |
+------------------+---------------------------------+---------------+---------------+
| `get_di_contact` | Read digital input contact type |               | (0:wet, 1:dry)|
+------------------+---------------------------------+---------------+---------------+
| `get_do_contact` | Read digital output contact type|               | (0:wet, 1:dry)|
+------------------+---------------------------------+---------------+---------------+