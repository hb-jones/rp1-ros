from trajectory_planners import *
#from low_level_controller import LowLevelController
from odometry_system import OdometrySystem
from rp1config import RP1Configuration
import logging
import logging.config


class RP1Controller(): 
    """High Level controller for whole system"""
    trajectory_planner: ControlMode
    def __init__(self):
        self.config = RP1Configuration()
        logging.config.fileConfig('logging.conf',disable_existing_loggers=False)#Configure root logger TODO remove as is in __init__ file
        logging.info(" - New Initialisation of logger \n")
        trajectory_planner = LocalVelocityControl(self)
        return

    def set_trajectory_planner(self, planner):
        """Sets trajectory planner. Planner must be an initialised Control Mode"""
        self.trajectory_planner = planner #TODO perhaps should construct object here
        
    def set_target(self, target: Target):
        self.trajectory_planner.input_target(target)
        return
