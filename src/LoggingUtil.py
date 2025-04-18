import sys
import logging
from datetime import datetime
from typing import Optional
from colorama import Fore

class LoggingUtil():
    def __init__(self, logger_mode, handler_mode):
        self.logger_mode = logger_mode
        self.handler_mode = handler_mode
        self.logger = None

    @staticmethod
    def _create_filename():
        return f"HX52x_session_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log"

    def _check_logger_mode(self):
        if self.logger_mode in [None, "off"]:
            print("Logger Mode off, ignoring")
            return None

        if self.logger_mode not in ['info', 'debug','error']:
            print("Logger Mode", self.logger_mode)
            raise ValueError("ERROR | Invalid logger_mode")

        return self.logger_mode

    def _create_handlers(self, filename):
        handlers = []
        if self.handler_mode == "both":
            handlers.extend([logging.FileHandler(filename), 
                             logging.StreamHandler(sys.stdout)])
        elif self.handler_mode == "console":
            handlers.append(logging.StreamHandler(sys.stdout))
        elif self.handler_mode == "file":
            handlers.append(logging.FileHandler(filename))
        else:
            raise ValueError("ERROR | Incorrect Handle Parameter Provided") 

        return handlers

    def _create_logger(self):# -> logging.RootLogger:
        '''Create Logger with INFO, DEBUG, and ERROR Debugging'''
        result = self._check_logger_mode()
        if result is None:
            return

        filename = self._create_filename()
        handlers = self._create_handlers(filename)

        self.logger = logging.getLogger()

        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }

        level = level_dict.get(self.logger_mode, "Unknown")

        if level == 'Unknown' or level is None:
            self.logger_mode = 'off'
            del self.logger
            raise ValueError("ERROR | Invalid logger_mode")

        logging.basicConfig (
            format='[%(asctime)s %(levelname)s %(filename)s:%(lineno)d -> %(funcName)s()] %(message)s',
            level=level,
            handlers=handlers  
        )

        self._log_print(f"Logger Initialized...",
                         print_to_console=False,
                         log=True,
                         level=logging.INFO
                        )

    def _lprint(self, message_info, print_to_console, color):
        if print_to_console and self.logger_mode != "console":
            if color == Fore.RED:
                print(Fore.RED + message_info)
            elif color == Fore.GREEN:
                print(Fore.GREEN + message_info)
            else:
                print(message_info)

    def _output_log(self, log_msg, level, stacklevel=3):
        if level == logging.INFO:
            self.logger.info(log_msg, stacklevel=stacklevel)
        elif level == logging.DEBUG:
            self.logger.debug(log_msg, stacklevel=stacklevel)
        elif level == logging.ERROR:
            self.logger.error(log_msg, stacklevel=stacklevel)
        else:
            raise ValueError("ERROR | INCORRECT MODE INPUT INTO LOGGER")

    def _log_print(self, message:str, print_to_console:bool=True, color:str=None, 
                    log:bool=False, level:Optional[int]=None) -> bool:

        self._lprint(message, print_to_console, color)

        if log is True \
                and level is not None \
                and self.logger_mode not in ["off", None]:

            self._output_log(message, level)