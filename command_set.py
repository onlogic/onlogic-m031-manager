from enum import IntEnum

################ Constants #################
MCU_VID_PID = "353F:A105"

# Hardcoded transmission values
SHELL_SOF  = 0x01
SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'
NUM_NACKS  = 255 + 4
RESPONSE_FRAME_LEN = 7

# Comport Check Values
NACKS_NEEDED = 5
TIME_THRESHOLD = 2.5


class ShellParams(IntEnum):
    # Hardcoded transmission values
    SHELL_SOF  = 0x01
    SHELL_ACK  = 0x0D # decimal 13, ascii equiv is '\r'
    SHELL_NACK = 0x07 # decimal 7, ascii equiv is '\a'
    NUM_NACKS  = 255 + 4
    RESPONSE_FRAME_LEN = 7

    # Comport Check Values
    NACKS_NEEDED = 5
    TIME_THRESHOLD = 2.5

# kinds
GET_DI = 0x20
SET_DO = 0x21
GET_DO = 0x22
GET_DI_CONTACT = 0x3F
GET_DO_CONTACT = 0x40
SET_DI_CONTACT = 0x41
SET_DO_CONTACT = 0x42


class Kinds(IntEnum):
    GET_DI = 0x20
    SET_DO = 0x21
    GET_DO = 0x22
    GET_DI_CONTACT = 0x3F
    GET_DO_CONTACT = 0x40
    SET_DI_CONTACT = 0x41
    SET_DO_CONTACT = 0x42

# Command Set adhering to shell format 
# header: sof, crc, len, kind; data
# CRC-8/SMBUS - https://crccalc.com/?crc=012003&method=CRC-8&datatype=hex&outtype=hex
get_di_commands = {
    0 : [SHELL_SOF, 0xC5, 1, GET_DI, 0],
    1 : [SHELL_SOF, 0xC2, 1, GET_DI, 1],
    2 : [SHELL_SOF, 0xCB, 1, GET_DI, 2],
    3 : [SHELL_SOF, 0xCC, 1, GET_DI, 3], # 0xCC = CRC_8_SMBUS of (0x01 0x20 0x03)
    4 : [SHELL_SOF, 0xD9, 1, GET_DI, 4],
    5 : [SHELL_SOF, 0xDE, 1, GET_DI, 5],
    6 : [SHELL_SOF, 0xD7, 1, GET_DI, 6],
    7 : [SHELL_SOF, 0xD0, 1, GET_DI, 7], 
}

get_do_commands = {
    0 : [SHELL_SOF, 0xEF, 1, GET_DO, 0],
    1 : [SHELL_SOF, 0xE8, 1, GET_DO, 1],
    2 : [SHELL_SOF, 0xE1, 1, GET_DO, 2],
    3 : [SHELL_SOF, 0xE6, 1, GET_DO, 3],
    4 : [SHELL_SOF, 0xF3, 1, GET_DO, 4],
    5 : [SHELL_SOF, 0xF4, 1, GET_DO, 5],
    6 : [SHELL_SOF, 0xFD, 1, GET_DO, 6],
    7 : [SHELL_SOF, 0xFA, 1, GET_DO, 7], # 0xCC = CRC_8_SMBUS of (0x01 0x20 0x03)
}


set_do_commands = {
    0 : [SHELL_SOF, 0x4, 2, SET_DO, 0, 0],
    1 : [SHELL_SOF, 0x2B, 1, SET_DO, 1, 0],
    2 : [SHELL_SOF, 0x14, 1, SET_DO, 2, 0],
    3 : [SHELL_SOF, 0x01, 1, SET_DO, 3, 0],
    4 : [SHELL_SOF, 0x39, 1, SET_DO, 0, 1],
    5 : [SHELL_SOF, 0x2C, 1, SET_DO, 1, 1],
    6 : [SHELL_SOF, 0x13, 1, SET_DO, 2, 1],
    7 : [SHELL_SOF, 0x06, 1, SET_DO, 3, 1],
}

# set_do_commands = {
#     0 : [SHELL_SOF, 0x3E, 1, SET_DO, 0, 0],
#     1 : [SHELL_SOF, 0x2B, 1, SET_DO, 1, 0],
#     2 : [SHELL_SOF, 0x14, 1, SET_DO, 2, 0],
#     3 : [SHELL_SOF, 0x01, 1, SET_DO, 3, 0],
#     4 : [SHELL_SOF, 0x39, 1, SET_DO, 0, 1],
#     5 : [SHELL_SOF, 0x2C, 1, SET_DO, 1, 1],
#     6 : [SHELL_SOF, 0x13, 1, SET_DO, 2, 1],
#     7 : [SHELL_SOF, 0x06, 1, SET_DO, 3, 1],
# }

'''
# TODO: POPULATE "N/A" with CRC8SMBUS Values

set_do_commands = {
    0 : {
        0 : [SHELL_SOF, 0x3E,  1, SET_DO, 0, 0],
        1 : [SHELL_SOF, 0x2B,  1, SET_DO, 1, 0],
        2 : [SHELL_SOF, 0x14,  1, SET_DO, 2, 0],
        3 : [SHELL_SOF, 0x01,  1, SET_DO, 3, 0],
        4 : [SHELL_SOF, "N/A", 1, SET_DO, 4, 0],
        5 : [SHELL_SOF, "N/A", 1, SET_DO, 5, 0],
        6 : [SHELL_SOF, "N/A", 1, SET_DO, 6, 0],
        7 : [SHELL_SOF, "N/A", 1, SET_DO, 7, 0],
    },
    1 : {
        0 : [SHELL_SOF, "N/A", 1, SET_DO, 0, 1],
        1 : [SHELL_SOF, "N/A", 1, SET_DO, 1, 1],
        2 : [SHELL_SOF, "N/A", 1, SET_DO, 2, 1],
        3 : [SHELL_SOF, "N/A", 1, SET_DO, 3, 1],
        4 : [SHELL_SOF, 0x39,  1, SET_DO, 4, 1],
        5 : [SHELL_SOF, 0x2C,  1, SET_DO, 5, 1],
        6 : [SHELL_SOF, 0x13,  1, SET_DO, 6, 1],
        7 : [SHELL_SOF, 0x06,  1, SET_DO, 7, 1],
    }
}
'''

get_di_contact_command = [SHELL_SOF, 0xA8, 1, GET_DI_CONTACT]

get_do_contact_command = [SHELL_SOF, 0xD2, 1, GET_DO_CONTACT]

set_di_contact_commands = {
    0 : [SHELL_SOF, 0x25, 1, SET_DI_CONTACT, 0],
    1 : [SHELL_SOF, 0x22, 1, SET_DI_CONTACT, 1],
}

set_do_contact_commands = {
    0 : [SHELL_SOF, 0x1A, 1, SET_DO_CONTACT, 0],
    1 : [SHELL_SOF, 0x1D, 1, SET_DO_CONTACT, 1],
}
############################################

# sof, crc, len, kind, data