# -*- coding: utf-8 -*-
"""

"""
import sys
import logging
from datetime import datetime
from typing import Optional

class LoggingUtil():
    def __init__(self, logger_name, logger_level, handler_mode):
        self.logger_name  = self.__handle_lconfig_str(logger_name)
        self.logger_level  = self.__handle_lconfig_str(logger_level)
        self.handler_mode = self.__handle_lconfig_str(handler_mode)
        self.logger = None
        self.format = '[%(asctime)s %(levelname)s %(filename)s:%(lineno)d -> %(funcName)s()] %(message)s'
    
    @staticmethod
    def __handle_lconfig_str(input_str: str) -> str | None:
        return input_str.lower().strip() if isinstance(input_str, str) else input_str

    @staticmethod
    def _create_filename():
        return f"log_session_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log"

    def _get_logger_level(self):
        if self.logger_level in [None, "off"]:
            print("Logger Mode off, ignoring")
            return None

        if self.logger_level not in ['info', 'debug','error']:
            print("Logger Mode", self.logger_level)
            raise ValueError("ERROR | Invalid logger_level")

        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }

        level = level_dict.get(self.logger_level, "Unknown")

        return level

    def _config_handlers(self, filename):
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

    def config_logger_elements(self) -> Optional[logging.Logger]: 
        level = self._get_logger_level()
        if level is None:
            # Get logger, ensure it's disabled or has no handlers
            logger = logging.getLogger(self.logger_name)
            logger.disabled = True 
            self.logger = logger
            return None # Return None if setup didn't happen

        logger = logging.getLogger(self.logger_name)
        logger.disabled = False # Ensure enabled if previously off

        logger.handlers.clear()

        if self.handler_mode in ['file', 'both']:
            filename = self._create_filename()
        else:
            filename = None
        
        handlers = self._config_handlers(filename)

        logger.setLevel(level)

        formatter = logging.Formatter(self.format)
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Add NullHandler if user requested mode resulted in no actual handlers
        if not handlers and self.handler_mode not in [None, "off"]:
            logger.addHandler(logging.NullHandler())
            print(f"Warning: No handlers for mode '{self.handler_mode}', added NullHandler to '{self.logger_name}'")

        # Set propagate = False after adding handlers
        logger.propagate = False

        self.logger = logger
        print(f"Configured logger '{self.logger_name}'"
              f"(Level: {self.logger_level.upper()}," 
              f"Handlers: {[h.__class__.__name__ for h in logger.handlers]}," 
              f"Propagate: {logger.propagate})")
        
        return logger