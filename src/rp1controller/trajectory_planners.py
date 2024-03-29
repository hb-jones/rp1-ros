from math import copysign, fabs
from time import sleep
import numpy as np
import time
from typing import Tuple
import logging, threading

class Target:    
    def __init__(self, local_velocity: Tuple[float, float] = (0,0), local_angular: float = 0):
        self.local_velocity = local_velocity    #Linear velocity in local frame
        self.angular_velocity  = local_angular  #Angular velocity
        self.world_velocity = (0,0)             #linear velocity target in world frame
        self.world_bearing  = 0                 #Bearing to face
        self.world_point = (0,0)                #Coordinate to move to
        self.world_point_facing = (0,0)         #Coordinate for platform to face 

    def __str__(self):
        return f"Local Velocity: {self.local_velocity}, Angular: {self.angular_velocity}, Position: {self.world_point}, Bearing: {self.world_bearing}"
    




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
        """Sets target"""
        self.target = target
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


class WorldPoseControl(ControlMode):
    """Parent controller using world pose and max speed/acceleration arguments.
    Moves directly to target pose rotating and translating at the same time"""
    name = "WorldPoseControl"

    loop_run_flag = False
    thread_handle = None 
    target: Target = None #Replace with coordinate and heading? TODO

    delay_time_target = 0.02 #Ideal Delay time for system to acheive
    delay_time_last = 0.02 #The last delay time, used when system is too slow.

    current_target_linear_velocity = (0,0)
    current_target_angular_velocity = 0

    slow_mode_displacement = 0.3 #If the target is this far away the robot will move more slowly.


    def __init__(self, hlc):
        super().__init__(hlc)
        self.localisation_system = self.hlc.localisation
        self.loop_run_flag = True
        self.thread_handle = threading.Thread(target = self.trajectory_loop, daemon= False)
        self.thread_handle.start()
        self.logger.info(" - Position Controller System Started")

    def __del__(self):
        self.loop_run_flag = False
        super().__del__()

    def trajectory_loop(self):
        while self.loop_run_flag:
            if self.target != None:
                if self.hlc.trajectory_planner != self:
                    print(f"Disabling planner: {self.name}")#TODO DEBUG PRINT
                    self.loop_run_flag = False
                    self.set_low_level_interface_target((0,0),0)
                    break

                self.configure_target()
                time_start = time.perf_counter()
                
                max_linear_velocity = self.hlc.config.linear_velocity_max
                safe_linear_velocity = self.hlc.config.linear_velocity_safe
                max_angular_velocity = self.hlc.config.angular_velocity_max
                current_pose = self.localisation_system.current_pose

                error_position = self.localisation_system.get_relative_position_of_point(self.target.world_point)


                
                target_velocity_max = (copysign(max_linear_velocity, error_position[0]), copysign(max_linear_velocity, error_position[1]))
                target_velocity_safe = (copysign(safe_linear_velocity, error_position[0]), copysign(safe_linear_velocity, error_position[1]))
                error_velocity = (target_velocity_max[0] - current_pose.world_x_velocity ,target_velocity_max[1] - current_pose.world_y_velocity)
                
                
                error_angle = self.localisation_system.get_relative_bearing_from_absolute_bearing(self.target.world_bearing)
                target_angular_velocity_max = copysign(max_angular_velocity, error_angle)
                error_angular_velocity = target_angular_velocity_max-current_pose.angular_velocity
                                
                target_world_x = 0
                target_world_y = 0
                target_angular = 0



                #X
                                
                if abs(error_position[0])<self.hlc.config.max_error_position and abs(current_pose.world_x_velocity)<self.hlc.config.max_error_velocity:
                    target_world_x = 0
                    #self.hlc.localisation.log_localisation(True)
                    #print("Close Enough!")
                
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_x_velocity)
                    
                    if stopping_distance>abs(error_position[0])-self.hlc.config.max_error_position and abs(error_velocity[0])<abs(target_velocity_max[0]):
                            target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                            #print("Decelerating to target")
                    elif abs(current_pose.world_x_velocity)>max_linear_velocity or self.current_target_linear_velocity[0]>max_linear_velocity:
                        target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                        #print("Overspeed")
                    elif abs(error_position[0])<self.slow_mode_displacement:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_safe[0], safe_mode=True)
                        #Accelerating Slowly
                    
                    else:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_max[0])
                        #print("Accelerating!")
                #Y
               
                if abs(error_position[1])<self.hlc.config.max_error_position and abs(current_pose.world_y_velocity)<self.hlc.config.max_error_velocity:
                    target_world_y = 0
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_y_velocity)
                    if stopping_distance>abs(error_position[1])-self.hlc.config.max_error_position and abs(error_velocity[1])<abs(target_velocity_max[1]):
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(current_pose.world_y_velocity)>max_linear_velocity or self.current_target_linear_velocity[1]>max_linear_velocity:
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(error_position[1])<self.slow_mode_displacement:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_safe[1], safe_mode=True)
                        #Accelerating Slowly
                    else:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_max[1])

                #print(f"Target WX: {target_world_x} target WY: {target_world_y}")

                #Angular
                
                if abs(error_angle)<self.hlc.config.max_error_bearing and abs(current_pose.angular_velocity)<self.hlc.config.max_error_angular_velocity:
                    #Close enough to target
                    target_angular = 0
                    
                else:
                    stopping_distance = self.get_stopping_distance_angular(current_pose.angular_velocity)
                    if stopping_distance>abs(error_angle)-self.hlc.config.max_error_bearing and abs(error_angular_velocity)<abs(target_angular_velocity_max):
                        #Decelerate
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    elif abs(current_pose.angular_velocity)>max_angular_velocity or self.current_target_angular_velocity>max_angular_velocity: 
                        #Stay below max speed
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    else:
                        #Accelerate
                        target_angular = self.accelerate_angular_step(self.current_target_angular_velocity, target_angular_velocity_max)



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
                
                self.delay_time_last = time.perf_counter()-time_start
                if self.delay_time_last > self.delay_time_target*1.1:
                    print(f"Last delay time {self.delay_time_last}s")
                if self.delay_time_last<self.delay_time_target: #If time taken was less than target then wait the rest of the time.
                    sleep(self.delay_time_target-self.delay_time_last)
                    self.delay_time_last = self.delay_time_target
            else:
                self.set_low_level_interface_target((0,0),0) #Stop if no valid target found
        return



    def configure_target(self): #Fixes the target for future TMS
        return

    def accelerate_linear_step(self, velocity, target_velocity, safe_mode = False):
        if safe_mode:
            acceleration_limit = self.hlc.config.acceleration_safe
        else:
            acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time_last

        stepped_velocity = velocity+step_size*copysign(1,target_velocity)
        return stepped_velocity


    def decelerate_linear_step(self, velocity):
        acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        return copysign(abs(velocity)-step_size, velocity) #Decrease magnitude of speed by step size

    def accelerate_angular_step(self, angular_velocity, target_angular_velocity):
        acceleration_limit = self.hlc.config.angular_acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        stepped_velocity = angular_velocity+step_size*copysign(1,target_angular_velocity)
        return stepped_velocity

    def decelerate_angular_step(self, angular_velocity):
        acceleration_limit = self.hlc.config.angular_acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        return copysign(abs(angular_velocity)-step_size, angular_velocity) #Decrease magnitude of speed by step size

    def input_target(self, target: Target):
        if not self.check_input(target): 
            self.target = None
            return False
        self.target = target
        self.current_target_linear_velocity = (self.localisation_system.current_pose.world_x_velocity, self.localisation_system.current_pose.world_y_velocity)
        self.current_target_angular_velocity = self.localisation_system.current_pose.angular_velocity
        self.x_polypath = None
        self.y_polypath = None
        self.a_polypath = None #Reset paths to be recalculated
        return True


    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_point == None or target.world_bearing == None:
            self.logger.error(" - {}:  input target missing world_point or world_bearing".format(self.name))
            return False
        return True

    def get_stopping_distance_linear(self, velocity):
        speed = abs(velocity)
        stopping_distance = (speed**2)/(2*self.hlc.config.acceleration_max)
        return stopping_distance

    def get_stopping_distance_angular(self, angular_velocity):
        angular_speed = abs(angular_velocity)
        stopping_distance = (angular_speed**2)/(2*self.hlc.config.angular_acceleration_max)
        return stopping_distance

class WorldPoseControlAggressive(WorldPoseControl):
    def trajectory_loop(self):
        while self.loop_run_flag:
            if self.target != None:
                if self.hlc.trajectory_planner != self:
                    print(f"Disabling planner: {self.name}")#TODO DEBUG PRINT
                    self.loop_run_flag = False
                    self.set_low_level_interface_target((0,0),0)
                    break

                self.configure_target()
                time_start = time.perf_counter()
                
                max_linear_velocity = self.hlc.config.linear_velocity_max
                safe_linear_velocity = self.hlc.config.linear_velocity_safe
                max_angular_velocity = self.hlc.config.angular_velocity_max
                current_pose = self.localisation_system.current_pose

                error_position = self.localisation_system.get_relative_position_of_point(self.target.world_point)


                
                target_velocity_max = (copysign(max_linear_velocity, error_position[0]), copysign(max_linear_velocity, error_position[1]))
                target_velocity_safe = (copysign(safe_linear_velocity, error_position[0]), copysign(safe_linear_velocity, error_position[1]))
                error_velocity = (target_velocity_max[0] - current_pose.world_x_velocity ,target_velocity_max[1] - current_pose.world_y_velocity)
                
                
                error_angle = self.localisation_system.get_relative_bearing_from_absolute_bearing(self.target.world_bearing)
                target_angular_velocity_max = copysign(max_angular_velocity, error_angle)
                error_angular_velocity = target_angular_velocity_max-current_pose.angular_velocity
                                
                target_world_x = 0
                target_world_y = 0
                target_angular = 0



                #X
                                
                if abs(error_position[0])<self.hlc.config.max_error_position and abs(current_pose.world_x_velocity)<self.hlc.config.max_error_velocity:
                    target_world_x = 0
                    #self.hlc.localisation.log_localisation(True)
                    #print("Close Enough!")
                
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_x_velocity)
                    
                    if stopping_distance>abs(error_position[0])-self.hlc.config.max_error_position and abs(error_velocity[0])<abs(target_velocity_max[0]):
                            target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                            #print("Decelerating to target")
                    elif abs(current_pose.world_x_velocity)>max_linear_velocity or self.current_target_linear_velocity[0]>max_linear_velocity:
                        target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                        #print("Overspeed")
                    elif abs(error_position[0])<self.slow_mode_displacement:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_safe[0], safe_mode=True)
                        #Accelerating Slowly
                    
                    else:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_max[0])
                        #print("Accelerating!")
                #Y
               
                if abs(error_position[1])<self.hlc.config.max_error_position and abs(current_pose.world_y_velocity)<self.hlc.config.max_error_velocity:
                    target_world_y = 0
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_y_velocity)
                    if stopping_distance>abs(error_position[1])-self.hlc.config.max_error_position and abs(error_velocity[1])<abs(target_velocity_max[1]):
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(current_pose.world_y_velocity)>max_linear_velocity or self.current_target_linear_velocity[1]>max_linear_velocity:
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(error_position[1])<self.slow_mode_displacement:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_safe[1], safe_mode=True)
                        #Accelerating Slowly
                    else:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_max[1])

                #print(f"Target WX: {target_world_x} target WY: {target_world_y}")

                #Angular
                
                if abs(error_angle)<self.hlc.config.max_error_bearing and abs(current_pose.angular_velocity)<self.hlc.config.max_error_angular_velocity:
                    #Close enough to target
                    target_angular = 0
                    
                else:
                    stopping_distance = self.get_stopping_distance_angular(current_pose.angular_velocity)
                    if stopping_distance>abs(error_angle)-self.hlc.config.max_error_bearing and abs(error_angular_velocity)<abs(target_angular_velocity_max):
                        #Decelerate
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    elif abs(current_pose.angular_velocity)>max_angular_velocity or self.current_target_angular_velocity>max_angular_velocity: 
                        #Stay below max speed
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    else:
                        #Accelerate
                        target_angular = self.accelerate_angular_step(self.current_target_angular_velocity, target_angular_velocity_max)



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
                
                self.delay_time_last = time.perf_counter()-time_start
                if self.delay_time_last > self.delay_time_target*1.1:
                    print(f"Last delay time {self.delay_time_last}s")
                if self.delay_time_last<self.delay_time_target: #If time taken was less than target then wait the rest of the time.
                    sleep(self.delay_time_target-self.delay_time_last)
                    self.delay_time_last = self.delay_time_target
            else:
                self.set_low_level_interface_target((0,0),0) #Stop if no valid target found
        return

#World Frame Pose Controllers - These are persistent and need a thread
class WorldPoseControlPoly(ControlMode):
    """Parent controller using world pose and max speed/acceleration arguments.
    Moves directly to target pose rotating and translating at the same time"""
    name = "WorldPoseControl"

    loop_run_flag = False
    thread_handle = None 
    target: Target = None #Replace with coordinate and heading? TODO

    delay_time_target = 0.02 #Ideal Delay time for system to acheive
    delay_time_last = 0.02 #The last delay time, used when system is too slow.

    current_target_linear_velocity = (0,0)
    current_target_angular_velocity = 0

    x_polypath = None
    x_polypath_index = 0
    y_polypath = None
    y_polypath_index = 0
    a_polypath = None
    a_polypath_index = 0

    def __init__(self, hlc):
        super().__init__(hlc)
        self.localisation_system = self.hlc.localisation
        self.loop_run_flag = True
        self.thread_handle = threading.Thread(target = self.trajectory_loop, daemon= False)
        self.thread_handle.start()
        self.logger.info(" - Position Controller System Started")

    def __del__(self):
        self.loop_run_flag = False
        self.thread_handle.join()
        super().__del__()

    def trajectory_loop(self):
        while self.loop_run_flag:
            if self.target != None:
                if self.hlc.trajectory_planner != self:
                    print(f"Disabling planner: {self.name}")#TODO DEBUG PRINT
                    self.loop_run_flag = False
                    self.set_low_level_interface_target((0,0),0)
                    break
                #TODO check if still active TMS
                self.configure_target()
                time_start = time.perf_counter()
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
                
                #TODO add look at point support here or in configure_target()
                error_angle = self.localisation_system.get_relative_bearing_from_absolute_bearing(self.target.world_bearing)
                target_angular_velocity_max = copysign(max_angular_velocity, error_angle)
                error_angular_velocity = target_angular_velocity_max-current_pose.angular_velocity
                                
                target_world_x = 0
                target_world_y = 0
                target_angular = 0



                #X
                if self.x_polypath is not None:
                    target_world_x = self.x_polypath[self.x_polypath_index]
                    self.x_polypath_index += 1
                    if self.x_polypath_index>=len(self.x_polypath):
                        self.x_polypath = None
                        self.x_polypath_index = 0
                
                elif abs(error_position[0])<self.hlc.config.max_error_position and abs(current_pose.world_x_velocity)<self.hlc.config.max_error_velocity:
                    target_world_x = 0
                    #self.hlc.localisation.log_localisation(True)
                    #print("Close Enough!")
                elif (abs(error_position[0])<self.hlc.config.polypath_distance) and (abs(current_pose.world_x_velocity)<self.hlc.config.polypath_max_speed):
                    #Create polynomial path
                    #may have issues with signs on velocity when going backwards near target TODO
                    #print("Generating path X")
                    self.x_polypath = self.generate_poly_path(self.hlc.config.polypath_time, 0, error_position[0], current_pose.world_x_velocity)
                    target_world_x = self.x_polypath[0]
                    self.x_polypath_index = 1
                
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_x_velocity)
                    
                    if stopping_distance>abs(error_position[0])-self.hlc.config.max_error_position and abs(error_velocity[0])<abs(target_velocity_max[0]):
                            target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                            #print("Decelerating to target")
                    elif abs(current_pose.world_x_velocity)>max_linear_velocity or self.current_target_linear_velocity[0]>max_linear_velocity:
                        target_world_x = self.decelerate_linear_step(self.current_target_linear_velocity[0])
                        #print("Overspeed")
                    else:
                        target_world_x = self.accelerate_linear_step(self.current_target_linear_velocity[0], target_velocity_max[0])
                        #print("Accelerating!")
                #Y
                if self.y_polypath is not None:
                    target_world_y = self.y_polypath[self.y_polypath_index]
                    self.y_polypath_index += 1
                    if self.y_polypath_index>=len(self.y_polypath):
                        self.y_polypath = None
                        self.y_polypath_index = 0
                elif abs(error_position[1])<self.hlc.config.max_error_position and abs(current_pose.world_y_velocity)<self.hlc.config.max_error_velocity:
                    target_world_y = 0
                elif (abs(error_position[1])<self.hlc.config.polypath_distance) and (abs(current_pose.world_y_velocity)<self.hlc.config.polypath_max_speed):
                    #Create polynomial path
                    #print("Generating path Y")
                    self.y_polypath = self.generate_poly_path(self.hlc.config.polypath_time, 0, error_position[1], current_pose.world_y_velocity)
                    target_world_y = self.y_polypath[0]
                    self.y_polypath_index = 1
                else:
                    stopping_distance = self.get_stopping_distance_linear(current_pose.world_y_velocity)
                    if stopping_distance>abs(error_position[1])-self.hlc.config.max_error_position and abs(error_velocity[1])<abs(target_velocity_max[1]):
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    elif abs(current_pose.world_y_velocity)>max_linear_velocity or self.current_target_linear_velocity[1]>max_linear_velocity:
                        target_world_y = self.decelerate_linear_step(self.current_target_linear_velocity[1])
                    else:
                        target_world_y = self.accelerate_linear_step(self.current_target_linear_velocity[1], target_velocity_max[1])

                #print(f"Target WX: {target_world_x} target WY: {target_world_y}")

                #Angular
                if self.a_polypath is not None:
                    #If there is a polynomial path
                    target_angular = self.a_polypath[self.a_polypath_index]
                    self.a_polypath_index += 1
                    if self.a_polypath_index>=len(self.a_polypath):
                        #End of path
                        self.a_polypath = None
                        self.a_polypath_index = 0
                elif abs(error_angle)<self.hlc.config.max_error_bearing and abs(current_pose.angular_velocity)<self.hlc.config.max_error_angular_velocity:
                    #Close enough to target
                    target_angular = 0
                elif (abs(error_angle)<self.hlc.config.polypath_distance) and (abs(current_pose.angular_velocity)<self.hlc.config.polypath_max_speed):
                    #Create polynomial path
                    #print("Generating path A") #TODO add specific angular configs
                    self.a_polypath = self.generate_poly_path(self.hlc.config.polypath_time, 0, error_angle, current_pose.angular_velocity)
                    target_angular = self.a_polypath[0]
                    self.a_polypath_index = 1
                else:
                    stopping_distance = self.get_stopping_distance_angular(current_pose.angular_velocity)
                    if stopping_distance>abs(error_angle)-self.hlc.config.max_error_bearing and abs(error_angular_velocity)<abs(target_angular_velocity_max):
                        #Decelerate
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    elif abs(current_pose.angular_velocity)>max_angular_velocity or self.current_target_angular_velocity>max_angular_velocity: 
                        #Stay below max speed
                        target_angular = self.decelerate_angular_step(self.current_target_angular_velocity)
                    else:
                        #Accelerate
                        target_angular = self.accelerate_angular_step(self.current_target_angular_velocity, target_angular_velocity_max)



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
                
                self.delay_time_last = time.perf_counter()-time_start
                if self.delay_time_last > self.delay_time_target*1.1:
                    print(f"Last delay time {self.delay_time_last}s")
                if self.delay_time_last<self.delay_time_target: #If time taken was less than target then wait the rest of the time.
                    sleep(self.delay_time_target-self.delay_time_last)
                    self.delay_time_last = self.delay_time_target
            else:
                self.set_low_level_interface_target((0,0),0) #Stop if no valid target found
        return

    def generate_poly_path(self, duration, position_start, position_end, speed_start, speed_end = 0, log = False):
        
        q0 = position_start
        qf = position_end
        v0 = speed_start
        vf = speed_end

        tf = duration
        t0 = 0
        
        #print(f"q0: {q0}, qf: {qf}, v0: {v0}, vf: {vf}, tf: {tf}")
        a0 = q0
        a1 = v0
        a2 = (3*(qf-q0)-(2*v0+vf)*tf)/(tf**2)
        a3 = (-2*(qf-q0)+(v0-vf)*tf)/(tf**3)
        T = np.arange(t0,tf,self.delay_time_target)
        V = []
        for t in T:
            v = a1+2*a2*t+3*a3*t**2
            V.append(v)
        path = V

        if log:
            self.logger.info(f"Generated path with max speed of {max(V)}m/s")
        return path


    def configure_target(self): #Fixes the target for future TMS
        return

    def accelerate_linear_step(self, velocity, target_velocity):
        acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time_last

        stepped_velocity = velocity+step_size*copysign(1,target_velocity)
        return stepped_velocity


    def decelerate_linear_step(self, velocity):
        acceleration_limit = self.hlc.config.acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        return copysign(abs(velocity)-step_size, velocity) #Decrease magnitude of speed by step size

    def accelerate_angular_step(self, angular_velocity, target_angular_velocity):
        acceleration_limit = self.hlc.config.angular_acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        stepped_velocity = angular_velocity+step_size*copysign(1,target_angular_velocity)
        return stepped_velocity

    def decelerate_angular_step(self, angular_velocity):
        acceleration_limit = self.hlc.config.angular_acceleration_max
        step_size = acceleration_limit*self.delay_time_last
        return copysign(abs(angular_velocity)-step_size, angular_velocity) #Decrease magnitude of speed by step size

    def input_target(self, target: Target):
        if not self.check_input(target): 
            self.target = None
            return False
        self.target = target
        self.current_target_linear_velocity = (self.localisation_system.current_pose.world_x_velocity, self.localisation_system.current_pose.world_y_velocity)
        self.current_target_angular_velocity = self.localisation_system.current_pose.angular_velocity
        self.x_polypath = None
        self.y_polypath = None
        self.a_polypath = None #Reset paths to be recalculated
        return True


    def check_input(self, target: Target):
        if not super().check_input(target): return False
        if target.world_point == None or target.world_bearing == None:
            self.logger.error(" - {}:  input target missing world_point or world_bearing".format(self.name))
            return False
        return True

    def get_stopping_distance_linear(self, velocity):
        speed = abs(velocity)
        stopping_distance = (speed**2)/(2*self.hlc.config.acceleration_max)
        return stopping_distance

    def get_stopping_distance_angular(self, angular_velocity):
        angular_speed = abs(angular_velocity)
        stopping_distance = (angular_speed**2)/(2*self.hlc.config.angular_acceleration_max)
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

