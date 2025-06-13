# -*- coding: utf-8 -*-
"""OnLogic M031 Manager Constants
    
This file contains constants used throughout the OnLogic M031 Manager.
It includes protocol constants, command kinds, status types, target indices,
and boundary types.

Frame format is as follows: 
    sof (1 Byte), crc (1 Byte), len (1 Byte), kind (1 Byte), data (O-8 Bytes), NACK (1 Byte) 
"""

class ProtocolConstants:
    """
    The ProtocolConstants class defines the baud-rate, DIO card device descriptor,
    transmission values, and serial check values used in the communication protocol with the DIO Card.


    Note:
        MAX_NACK_CLEARANCES number isn't magic.  In the worst possible case, the MCU may have an
        entire maximum-length frame buffered containing only SHELL_NACK.  To be
        confident that we've received the entire frame and the MCU is ready to accept
        our next command, we need to receive 4 bytes (header) + 255 bytes (payload) of
        NACKs. This said, we have yet to implement the the worst-case scenario in Python Package.
    """
    BAUDRATE = 115_200

    # DIO card Device Descriptior, VID and PID
    DIO_MCU_VID_PID_CDC = "353F:A105" 
    TIME_THRESHOLD = 2.5
    STANDARD_DELAY = .003
    STANDARD_NACK_CLEARANCES = 64
    MAX_NACK_CLEARANCES = 255 + 4  # 255 bytes of payload [MAX] + 4 bytes of header

    # Hardcoded transmission values
    SHELL_SOF  = 0x01
    SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
    SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'

    # Serial Check Values    
    NUM_NACKS  = 255 + 4
    RESPONSE_FRAME_LEN = 7
    NACKS_NEEDED = 5

class Kinds:
    """
    The Kinds class categorizes the command classifiers for automotive and DIO commands,
    providing a clear mapping of command types to their respective identifiers.

    The message kind can indicate:
        1. That a message was an error
        2. How to decode the incoming body data
    """
    # Automotive Command Classifiers
    ERR_ZERO_KIND = 0x00
    GET_INPUT_VOLTAGE = 0x01
    GET_IGNITION_STATE = 0x02
    GET_FIRMWARE_VERSION = 0x03
    GET_AUTOMOTIVE_MODE  = 0x06
    SET_AUTOMOTIVE_MODE  = 0x07
    GET_LOW_POWER_ENABLE = 0x08
    SET_LOW_POWER_ENABLE = 0x09
    GET_LOW_VOLTAGE_TIMER = 0x10
    SET_LOW_VOLTAGE_TIMER = 0x11
    GET_SHUTDOWN_VOLTAGE = 0x12
    SET_SHUTDOWN_VOLTAGE = 0x13 
   
    GET_START_UP_TIMER = 0x0A
    SET_START_UP_TIMER = 0x0B
    GET_SOFT_OFF_TIMER = 0x0C
    SET_SOFT_OFF_TIMER = 0x0D
    GET_HARD_OFF_TIMER = 0x0E
    SET_HARD_OFF_TIMER = 0x0F
    
    # DIO Command Classifiers
    GET_DI = 0x20
    SET_DO = 0x21
    GET_DO = 0x22
    SET_DO_CONTACT = 0x53
    GET_DO_CONTACT = 0x51
    SET_DI_CONTACT = 0x52
    GET_DI_CONTACT = 0x50

class StatusTypes:
    '''
    The StatusTypes class enumerates the various status codes that can be returned
    during the lifespan of the communication process, indicating success (0) 
    or different types of errors (< 0).
    '''
    SUCCESS = 0
    SEND_CMD_FAILURE = -1
    RECV_UNEXPECTED_PAYLOAD_ERROR = -2
    RECV_FRAME_NACK_ERROR = -3
    RECV_FRAME_CRC_ERROR = -4
    RECV_FRAME_ACK_ERROR = -5
    RECV_FRAME_SOF_ERROR = -6
    RECV_PARTIAL_FRAME_VALIDATION_ERROR = -7
    RECV_FRAME_VALUE_ERROR = -8
    FORMAT_NONE_ERROR = -9

class TargetIndices:
    '''    
    The TargetIndices class defines indices used to isolate target data within received frames,
    '''
    PENULTIMATE = -2
    RECV_PAYLOAD_LEN = 2
    PAYLOAD_START = 4

    SOF = 0
    CRC = 1
    LEN = 2
    KIND = 3
    NACK = -1  # NACK is the last byte in the frame

class BoundaryTypes:
    '''
    The BoundaryTypes class specifies numeric boundaries for command parameters,
    such as binary values, digital I/O pin ranges, decimal values, and byte values
    '''
    BASE_FRAME_SIZE = 4

    # Numeric boundries for various command parameters)
    BINARY_VALUE_RANGE = (0, 1)
    DIGITAL_IO_PIN_RANGE = (0, 7)
    DECIMAL_VALUE_RANGE = (0, 9)
    BYTE_VALUE_RANGE = (0, 255)

    AUTOMOTIVE_TIMER_RANGE = (1, 36_000)
    AUTOMOTIVE_SHUTDOWN_VOLTAGE_RANGE = (1.0, 48.0)

############################################
