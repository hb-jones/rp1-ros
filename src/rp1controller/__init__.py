#from rp1controller import RP1Controller

#Set up the root logger
import logging
import logging.config
logging.config.fileConfig('rp1controller/logging.conf',disable_existing_loggers=False)

from .rp1interface import RP1Controller