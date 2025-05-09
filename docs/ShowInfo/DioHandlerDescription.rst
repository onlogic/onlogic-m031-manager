Info: Digital input/ouput. The DIO module can be configured in two modes:

1. Wet contact mode: To function properly, dio should be connected to
    external power and ground. The Digital Outputs are "Open Collector" in wet contact mode, 
    and must be tied to VIN (+) with a resitor to source current. The load should not exceed 150 mA.
    Voltage ranges are between 7 V to 45 V. The contact modes in this type should be set to 0. So pass
    the contact type as 0 to the set-di-contact and set-do-contact commands.

    Setup required for Output:
        Vin + GND + Pull up (10kOhm acceptable).

2. Dry contact mode: Voltage is provided by system by defaulting to DOut external at 12V 
    but diode causes the voltage to drop to 11.2 V - 11.4 V. 
    
    Setup required for Output:
        Shared GND

Pinout:

```
---------------------------------------------------------------------
||  _     _     _     _     _     _     _     _     _     _     _  ||
|| |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Input
|| INT | DI8 | DI7 | DI6 | DI5 | DI4 | DI3 | DI2 | DI1 | DI0 |  -  ||
---------------------------------------------------------------------
||  _     _     _     _     _     _     _     _     _     _     _  ||
|| |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Output
|| GND | DO8 | DO7 | DO6 | DO5 | DO4 | DO3 | DO2 | DO1 | DO0 |  +  ||
---------------------------------------------------------------------
```


**Command Summary**

| Command      | Description                                  | Parameters                                       | Returns                     |
|--------------|----------------------------------------------|--------------------------------------------------|-----------------------------|
| `get_di`     | Read digital input state                     | pin val (0-7)                                    | (0:low, 1:high)             |
| `get_do`     | Read digital output state                    | pin val (0-7)                                    | (0:low, 1:high)             |
| `set_di`     | Set digital input state                      | pin val (0-7) \| state (0:low, 1:high)           | status                      |
| `set_do`     | Set digital output state                     | pin val (0-7) \| state (0:low, 1:high)           | status                      |
| `set_all_do` | Set all digital output state                 | list of desired pin states                       | status list                 |
| `get_all_do` | Read all digital output state                |                                                  | list of pin states          |
| `get_all_di` | Read all digital input state                 |                                                  | list of pin states          |
| `get_all_dio`| Read all digital input/output state          |                                                  | list of pin states          |

**Parameter Summary For Contact Modes**

| Command          | Description                         | Parameters          | Returns          |
|------------------|-------------------------------------|---------------------|------------------|
| `set_di_contact` | Set digital input contact type    | (0:wet, 1:dry)      |                  |
| `set_do_contact` | Set digital output contact type   | (0:wet, 1:dry)      |                  |
| `get_di_contact` | Read digital input contact type   |                     | (0:wet, 1:dry)   |
| `get_do_contact` | Read digital output contact type  |                     | (0:wet, 1:dry)   |