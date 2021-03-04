from typing import Tuple
import logging
if __name__ == "__main__": #TODO this is dirty af and probably shoudnt exist
    from rp1controller import RP1Controller
else:
    RP1Controller = object

#TODO Target struct, potentially replace with dictionary, using typing.NewType?
class Target:
    local_velocity = None
    local_angular  = None
    world_velocity = None
    world_heading  = None
    world_pose     = None
    world_pose_dir = None
    
    def __init__(self, local_velocity: Tuple[float, float] = None, local_angular: float = None):
        self.local_velocity = local_velocity
        self.local_angular  = local_angular
        return 
    






#Parent Class
class ControlMode:
    """Parent class for control modes. All control modes take a target object as an input and return local velocity and angular velocity targets"""
    name = "prototype"

    def __init__(self, hlc: RP1Controller):
        self.hlc = hlc
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        return
    def input_target(self, target: Target): 
        """Sets target""" #TODO fix docstring using https://numpydoc.readthedocs.io/en/latest/example.html#example
        self.logger.warning(" - ControlMode prototype: Unable to set target")
        return

    def check_input(self, target: Target):
        if type(target) != Target:
            self.logger.error(" - {} input was not of type Target".format(self.name))
            return False
        return True

    def output_target(self, linear, angular):
        """Sends target LV to LLI"""
        return

#Local Frame Velocity Controllers
class LocalVelocityControl(ControlMode):
    """Basic controller using local linear and angular velocity directly."""
    name = "LocalVelocityControl"

    def input_target(self, target: Target):
        """Sets target"""
        if not self.check_input(target): return False
        self.output_target(target.local_velocity, target.local_angular)
        return True

    def check_input(self, target: Target):
        super().check_input(target)
        if target.local_velocity == None or target.local_angular == None:
            self.logger.error(" - {}:  input target does not include local_velocity or local_angular".format(self.name))
            return False
        return True

#World Frame Velocity Controllers
class WorldVelocityControl(ControlMode):
    """Takes desired heading and velocity in the world frame"""
    pass
class WVTrackPositionControl(WorldVelocityControl):
    """WV controller that tracks a target coordinate"""
    pass
class WVTrackHeadingControl(WorldVelocityControl):
    """WV controller that tracks a target heading"""
    pass

#World Frame Pose Controllers - These are persistent and need a thread
class WorldPoseControl(ControlMode):
    """Parent controller using world pose and max speed/acceleration arguments.
    Moves directly to target pose rotating and translating at the same time"""
    pass
class WPTurnStraightTurnControl(WorldPoseControl):
    """WP controller that turns, moves forward then turns to final pose."""
    pass
class WPTrackPositionControl(WorldPoseControl):
    """WP controller that tracks a target coordinate while translating"""
    pass
class WPTrackHeadingControl(WorldPoseControl):
    """WP controller that tracks a target heading while translating"""
    pass

