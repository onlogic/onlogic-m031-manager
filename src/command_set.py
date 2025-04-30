################ Constants #################

class ProtocolConstants:
    BAUDRATE=115200

    # DIO card Device Descriptior, VID and PID
    DIO_MCU_VID_PID_CDC = "353F:A105" 
    TIME_THRESHOLD = 2.5
    STANDARD_DELAY = .004
    STANDARD_NACK_CLEARANCES = 64

    # Hardcoded transmission values
    SHELL_SOF  = 0x01
    SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
    SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'

    # Serial Check Values    
    NUM_NACKS  = 255 + 4
    RESPONSE_FRAME_LEN = 7
    NACKS_NEEDED = 5 

class Kinds:
    # Automotive Command Classifiers
    ERR_ZERO_KIND = 0x00
    GET_INPUT_VOLTAGE = 0x01
    GET_IGNITION_STATE = 0x02
    GET_FIRMWARE_VERSION = 0x03
    GET_AUTOMOTIVE_MODE  = 0x06
    SET_AUTOMOTIVE_MODE  = 0x07
    GET_LOW_POWER_ENABLE = 0x08
    SET_LOW_POWER_ENABLE = 0x09
    GET_START_UP_TIMER = 0x0A
    SET_START_UP_TIMER = 0x0B
    GET_SOFT_OFF_TIMER = 0x0C
    SET_SOFT_OFF_TIMER = 0x0D
    GET_HARD_OFF_TIMER = 0x0E
    SET_HARD_OFF_TIMER = 0x0F
    GET_LOW_VOLTAGE_TIMER = 0x10
    SET_LOW_VOLTAGE_TIMER = 0x11
    GET_SHUTDOWN_VOLTAGE = 0x12
    SET_SHUTDOWN_VOLTAGE = 0x13

    # DIO Command Classifiers
    GET_DI = 0x20
    SET_DO = 0x21
    GET_DO = 0x22
    SET_DO_CONTACT = 0x53
    GET_DO_CONTACT = 0x51
    SET_DI_CONTACT = 0x52
    GET_DI_CONTACT = 0x50

class StatusTypes:
    SUCCESS = 0
    SEND_CMD_FAILURE = -1
    RECV_UNEXPECTED_PAYLOAD_ERROR = -2
    RECV_FRAME_NACK_ERROR = -3
    RECV_FRAME_CRC_ERROR = -4
    RECV_FRAME_ACK_ERROR = -5
    RECV_FRAME_SOF_ERROR = -6

class TargetIndices:
    PENULTIMATE = -2
    RECV_PAYLOAD_LEN = 2
    PAYLOAD_START = 4

class BoundryTypes:
    BASE_FRAME_SIZE = 4 
    # Numeric boundries for various command parameters
    DIGITAL_INPUT_PIN_RANGE = (0, 7)
    DIGITAL_OUTPUT_PIN_RANGE = (0, 7)
    BINARY_OUTPUT_PIN_RANGE = (0, 1)
    DECIMAL_CODED_NUM_RANGE = (0, 9)

############################################
# sof, crc, len, kind, data