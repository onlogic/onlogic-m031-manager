from command_set import ProtocolConstants, Kinds, StatusTypes
from OnLogicNuvotonManager import OnLogicNuvotonManager
import time 
import logging

class AutomotiveHandler(OnLogicNuvotonManager):
    def __init__(self):
        super().__init__()

    