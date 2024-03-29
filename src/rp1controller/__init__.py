#from rp1controller import RP1Controller

#Set up the root logger
import logging
import logging.config
logging.addLevelName(8, "TELEM")
logging.config.fileConfig('rp1controller/logging.conf',disable_existing_loggers=False)

from .rp1interface import RP1Controller
from .trajectory_planners import Target
from .communications import RP1Server, RP1Client