import logging
import logging.config
from .trajectory_planners import ControlMode, Target



class RP1Controller(): 
    """High Level controller for whole system"""
    trajectory_planner = None
    low_level_interface = None
    def __init__(self):
        from .low_level_interface import LowLevelInterface
        from .odometry_system import LocalisationSystem
        from .trajectory_planners import LocalVelocityControl
        from .rp1config import RP1Configuration
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        self.config: RP1Configuration = RP1Configuration()
        self.logger.info(" - New Initialisation of logger \n")
        self.trajectory_planner = LocalVelocityControl(self)
        self.low_level_interface = LowLevelInterface(self)
        self.low_level_interface.start_loop()
        self.localisation = LocalisationSystem(self)
        
        return

    def set_trajectory_planner(self, planner: ControlMode):
        """Sets trajectory planner. Planner must be an initialised Control Mode"""
        self.logger.info(f" - Changing trajectory planner to {planner.name}")
        self.trajectory_planner = planner #TODO perhaps should construct object here
        
    def set_target(self, target):
        target: Target
        self.trajectory_planner.input_target(target)
        return
