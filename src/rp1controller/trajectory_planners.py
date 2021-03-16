from math import fabs
from typing import Tuple
import logging

#TODO Target struct, potentially replace with dictionary, using typing.NewType?
class Target:
    local_velocity = None
    local_angular  = None
    world_velocity = None
    world_heading  = None
    world_pose     = None
    world_pose_facing = None #Coordinate for platform to face
    
    def __init__(self, local_velocity: Tuple[float, float] = (0,0), local_angular: float = 0):
        self.local_velocity = local_velocity
        self.local_angular  = local_angular
        return 
    






#Parent Class
class ControlMode:
    """Parent class for control modes. All control modes take a target object as an input and return local velocity and angular velocity targets"""
    name = "prototype"

    def __init__(self, hlc):
        from .rp1interface import RP1Controller
        self.hlc: RP1Controller = hlc
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        self.logger.info(" - Trajectory Planner Started")
        return
    def input_target(self, target: Target): 
        """Sets target""" #TODO fix docstring using https://numpydoc.readthedocs.io/en/latest/example.html#example
        self.logger.warning(" - ControlMode prototype: Unable to set target")
        return

    def check_input(self, target: Target):
        if type(target) != Target:
            self.logger.error(" - {} input was not of type Target".format(self.name))
            return False
        #TODO Add speed limit checking
        return True

    def set_low_level_interface_target(self, linear, angular):
        """Sends target LV to LLI"""
        self.hlc.low_level_interface.set_target(linear, angular)
        return True

#Local Frame Velocity Controllers
class LocalVelocityControl(ControlMode):
    """Basic controller using local linear and angular velocity directly."""
    name = "LocalVelocityControl"

    def input_target(self, target: Target):
        """Sets target"""
        if not self.check_input(target): return False
        self.set_low_level_interface_target(target.local_velocity, target.local_angular)
        return True

    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.local_velocity == None or target.local_angular == None:
            self.logger.error(" - {}:  input target missing local_velocity or local_angular".format(self.name))
            return False
        return True

#World Frame Velocity Controllers
class WorldVelocityControl(ControlMode):
    """Takes desired angular velocity and linear velocity in the world frame"""
    name = "WorldVelocityControl"
    def input_target(self, target: Target):
        """Sets target"""
        if not self.check_input(target): return False
        self.set_low_level_interface_target(self.hlc.localisation.transform_WV_to_LV(target.world_velocity),target.local_angular)
        return True

    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_velocity == None or target.local_angular == None:
            self.logger.error(" - {}:  input target missing world_velocity or local_angular".format(self.name))
            return False
        return True

    
class WVTrackPositionControl(WorldVelocityControl): #TODO maybe these should not inherit from WVC? Just CM instead
    """WV controller that tracks a target coordinate"""
    pass
class WVTrackHeadingControl(WorldVelocityControl):
    """WV controller that tracks a target heading"""
    pass

#World Frame Pose Controllers - These are persistent and need a thread
class WorldPoseControl(ControlMode):
    """Parent controller using world pose and max speed/acceleration arguments.
    Moves directly to target pose rotating and translating at the same time"""
    name = "WorldPoseControl"
    def input_target(self, target: Target):
        if not self.check_input(target): return False
        #Generate desired X and Y speed based on current speed and acceleration limits

        #Find angular speed based on rotational error, angular velocity and max angular acceleration.

        self.set_low_level_interface_target()
    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_pose == None or target.local_angular == None:
            self.logger.error(" - {}:  input target missing world_velocity or local_angular".format(self.name))
            return False
        return True


class WPTurnStraightTurnControl(WorldPoseControl):
    """WP controller that turns, moves forward then turns to final pose."""
    pass
class WPTrackPositionControl(WorldPoseControl):
    """WP controller that tracks a target coordinate while translating"""
    pass
class WPTrackHeadingControl(WorldPoseControl):
    """WP controller that tracks a target heading while translating"""
    pass

