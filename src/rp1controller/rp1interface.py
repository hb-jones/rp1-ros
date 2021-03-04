import logging
import logging.config
from .trajectory_planners import Target



class RP1Controller(): 
    """High Level controller for whole system"""
    trajectory_planner = None
    low_level_interface = None
    def __init__(self):
        from .low_level_interface import LowLevelInterface
        from .trajectory_planners import LocalVelocityControl
        from .rp1config import RP1Configuration

        self.config: RP1Configuration = RP1Configuration()
        #logging.config.fileConfig('logging.conf',disable_existing_loggers=False)#Configure root logger TODO remove as is in __init__ file
        logging.info(" - New Initialisation of logger \n")
        trajectory_planner = LocalVelocityControl(self)
        self.low_level_interface = LowLevelInterface(self)
        self.low_level_interface.start_loop()
        
        return

    def set_trajectory_planner(self, planner):
        """Sets trajectory planner. Planner must be an initialised Control Mode"""
        self.trajectory_planner = planner #TODO perhaps should construct object here
        
    def set_target(self, target):
        target: Target
        self.trajectory_planner.input_target(target)
        return
