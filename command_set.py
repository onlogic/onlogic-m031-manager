

################ Constants #################
MCU_VID_PID = "353F:A105"
TIME_THRESHOLD = 2.5

class ProtocolConstants:
    # Hardcoded transmission values
    SHELL_SOF  = 0x01
    SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
    SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'
    NUM_NACKS  = 255 + 4
    RESPONSE_FRAME_LEN = 7
    NACKS_NEEDED = 5 # Comport Check Values    

class Kinds:
    GET_DI = 0x20
    SET_DO = 0x21
    GET_DO = 0x22
    SET_DO_CONTACT = 0x23
    GET_DO_CONTACT = 0x24
    SET_DI_CONTACT = 0x25
    GET_DI_CONTACT = 0x26

'''
class ErrorTypes:
    RECV_NONBINARY_DATATYPE_DETECTED = -1
    RECV_FRAME_CONFIRMATION_FAILURE = -2

    AKNOWLEDGEMENT_ERROR = -4


'''

############################################

# sof, crc, len, kind, data