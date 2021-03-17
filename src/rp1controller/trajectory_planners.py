from math import copysign, fabs
from time import sleep
from typing import Tuple
import logging, threading

class Target:
    local_velocity = None #Linear velocity in local frame
    angular_velocity  = None # angular velocity
    world_velocity = None #linear velocity target in world frame
    world_bearing  = None #Bearing to face
    world_point     = None #Coordinate to move to
    world_point_facing = None #Coordinate for platform to face
    
    def __init__(self, local_velocity: Tuple[float, float] = (0,0), local_angular: float = 0):
        self.local_velocity = local_velocity
        self.angular_velocity  = local_angular
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
        self.set_low_level_interface_target(target.local_velocity, target.angular_velocity)
        return True

    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.local_velocity == None or target.angular_velocity == None:
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
        self.set_low_level_interface_target(self.hlc.localisation.transform_WV_to_LV(target.world_velocity),target.angular_velocity)
        return True

    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_velocity == None or target.angular_velocity == None:
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

    loop_run_flag = False
    thread_handle = None 
    target: Target = None #Replace with coordinate and heading? TODO

    delay_time = 0.02

    current_target_linear_velocity = (0,0)
    current_target_angular_velocity = 0

    def __init__(self, hlc):
        super().__init__(hlc)
        self.localisation_system = self.hlc.localisation
        self.loop_run_flag = True
        self.thread_handle = threading.Thread(target = self.trajectory_loop, daemon= True)
        self.thread_handle.start()
        self.logger.info(" - Position Controller System Started")

    def __del__(self):
        self.loop_run_flag = False
        self.thread_handle.join()
        super().__del__()

    def trajectory_loop(self): #TODO this is just gonna accelerate it whatever direction
        while self.loop_run_flag:
            sleep(self.delay_time) #TODO change this to something to account for processing time
            if self.target != None:
                self.configure_target()
                #print("\n\n\n")
                #print(f"Target currently at position: {self.target.world_point}, bearing: {self.target.world_bearing}")
                #print(f"Robot Currently at position:  {(self.localisation_system.current_pose.world_x_position,self.localisation_system.current_pose.world_y_position)}, bearing: {self.target.world_bearing}")
                max_linear_velocity = self.hlc.config.linear_velocity_max
                max_angular_velocity = self.hlc.config.angular_velocity_max
                current_pose = self.localisation_system.current_pose

                error_position = self.localisation_system.get_relative_position_of_point(self.target.world_point)
                target_velocity_max = (copysign(max_linear_velocity, error_position[0]), copysign(max_linear_velocity, error_position[1]))
                error_velocity = (target_velocity_max[0] - current_pose.world_x_velocity ,target_velocity_max[1] - current_pose.world_y_velocity)
                #print(f"Positional error: {error_position}, Target Velocity Max: {target_velocity_max}, Velocity error: {error_velocity}")
                target_world_x = 0
                target_world_y = 0
                target_angular = 0

                #X
                if abs(error_position[0])<self.hlc.config.max_error_position and abs(current_pose.world_x_velocity)<self.hlc.config.max_error_velocity:
                    target_world_x = 0
                    #print("Close Enough!")
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_x_velocity)
                    print(f"Distance to target: {error_position[0]}, stopping distance: {stopping_distance}")
                    if stopping_distance>abs(error_position[0]) and abs(error_velocity[0])<abs(target_velocity_max[0]):
                            target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                            #print("Decelerating to target")
                    elif abs(current_pose.world_x_velocity)>max_linear_velocity or self.current_target_linear_velocity[0]>max_linear_velocity:
                        target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                        #print("Overspeed")
                    else:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_max[0])
                        #print("Accelerating!")

                #Y
                if abs(error_position[1])<self.hlc.config.max_error_position and abs(current_pose.world_y_velocity)<self.hlc.config.max_error_velocity:
                    target_world_y = 0
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_y_velocity)
                    if stopping_distance>abs(error_position[1]) and abs(error_velocity[1])<abs(target_velocity_max[1]):
                            target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(current_pose.world_y_velocity)>max_linear_velocity or self.current_target_linear_velocity[1]>max_linear_velocity:
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    else:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_max[1])

                #print(f"Target WX: {target_world_x} target WY: {target_world_y}")

                #Angular #TODO
                

                self.current_target_linear_velocity = (target_world_x,target_world_y)
                self.current_target_angular_velocity = target_angular
                #FINAL ERROR CHECKING
                target_local_x, target_local_y = self.localisation_system.transform_WV_to_LV((target_world_x, target_world_y))
                if abs(target_local_x)>max_linear_velocity: target_local_x = copysign(max_linear_velocity, target_local_x)
                if abs(target_local_y)>max_linear_velocity: target_local_y = copysign(max_linear_velocity, target_local_y)
                if abs(target_angular)>max_angular_velocity: target_angular = copysign(max_angular_velocity, target_angular)
                
                #print(f"Output is X: {target_local_x}, Y: {target_local_y}, A: {target_angular}")
                #print()

                self.set_low_level_interface_target((target_local_x, target_local_y),target_angular)
                

            else:
                self.set_low_level_interface_target((0,0),0) #Stop if no valid target found
        return

    def configure_target(self): #Fixes the target for future TMS
        return

    def accelerate_linear_step(self, velocity, target_velocity):
        acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time

        stepped_velocity = velocity+step_size*copysign(1,target_velocity)
        return stepped_velocity


    def decelerate_linear_step(self, velocity):
        acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time
        return copysign(abs(velocity)-step_size, velocity) #Decrease magnitude of speed by step size

    def input_target(self, target: Target):
        if not self.check_input(target): 
            self.target = None
            return False
        self.target = target
        self.current_target_linear_velocity = (self.localisation_system.current_pose.world_x_velocity, self.localisation_system.current_pose.world_y_velocity)
        self.current_target_angular_velocity = self.localisation_system.current_pose.angular_velocity
        return True


    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_point == None or target.world_bearing == None:
            self.logger.error(" - {}:  input target missing world_velocity or world_bearing".format(self.name))
            return False
        return True

    def get_stopping_distance_linear(self, velocity):
        speed = abs(velocity)
        stopping_distance = (speed**2)/(2*self.hlc.config.acceleration_max)
        return stopping_distance


class WPTurnStraightTurnControl(WorldPoseControl):
    """WP controller that turns, moves forward then turns to final pose."""
    pass
class WPTrackPositionControl(WorldPoseControl):
    """WP controller that tracks a target coordinate while translating"""
    pass
class WPTrackHeadingControl(WorldPoseControl):
    """WP controller that tracks a target heading while translating"""
    pass

