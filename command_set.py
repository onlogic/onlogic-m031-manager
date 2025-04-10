################ Constants #################

class ProtocolConstants:
    MCU_VID_PID = "353F:A105"
    TIME_THRESHOLD = 2.5

    # Hardcoded transmission values
    SHELL_SOF  = 0x01
    SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
    SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'

    # Serial Check Values    
    NUM_NACKS  = 255 + 4
    RESPONSE_FRAME_LEN = 7
    NACKS_NEEDED = 5 

class Kinds:
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
    RECV_NONBINARY_DATATYPE_DETECTED = -2
    RECV_FRAME_NACK_ERROR = -3
    RECV_FRAME_CRC_ERROR = -4
    RECV_FRAME_ACK_ERROR = -5
    RECV_FRAME_SOF_ERROR = -6

############################################
# sof, crc, len, kind, data