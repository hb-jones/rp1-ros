import logging, time, threading
from math import cos, pi, sin, atan2

from .rp1interface import RP1Controller

class LocalisationSystem():
    loop_run_flag = True
    thread_handle = None
    output_function = None #Function to output telemetry (such as to ROS node). May use polling based system instead as in LLI

    current_pose = None
    localisation_last_updated_time = 0

    def __init__(self, main_controller: RP1Controller):
        self.main_controller = main_controller
        self.LLI = self.main_controller.low_level_interface
        self.telemetry_logger = logging.getLogger('telem') #Setup telemetry logging
        self.logger = logging.getLogger(__name__)
        
        self.telemetry_logger.log(8, "")
        self.telemetry_logger.log(8, "Time, Xpos, Ypos, heading, XLvel, YLvel, RLvel")
        self.current_pose = VelocityPose()
        self.thread_handle = threading.Thread(target = self.localisation_loop)
        self.thread_handle.start()
        self.logger.info(" - Localisation System Started")
        return

    def __del__(self):
        self.loop_run_flag = False
        if self.thread_handle != None:
            self.thread_handle.join()
        

    def localisation_loop(self):
        loop_counter = 0
        while (self.loop_run_flag):
            if self.LLI.odom_updated_time != self.localisation_last_updated_time:
                loop_counter += 1
                self.update_localisation()
                if loop_counter > 100 or True: #TODO maybe log every cycle
                    loop_counter = 0
                    self.log_localisation(False) #Set tp true for console logging
            time.sleep(0.02) #TODO if this fixes issues then remove 
    def update_localisation(self):
        LLI = self.LLI
        timestamp = LLI.odom_updated_time
        v_linear = LLI.odom_linear
        v_angular = LLI.odom_angular

        time_delta = timestamp - self.current_pose.timestamp

        heading_delta = time_delta*v_angular
        new_heading = self.convert_angle_to_bearing(self.current_pose.heading+heading_delta)

        #Movement based on new heading, may be better to base on halfway between old and new
        world_x_vel, world_y_vel = self.transform_LV_to_WV(v_linear, new_heading)

        x_delta = world_x_vel*time_delta
        new_x_pos = x_delta+self.current_pose.world_x_position

        y_delta = world_y_vel*time_delta
        new_y_pos = y_delta+self.current_pose.world_y_position

        velocitypose = VelocityPose()
        velocitypose.timestamp =timestamp
        velocitypose.local_x_velocity = v_linear[0]
        velocitypose.local_y_velocity = v_linear[1]
        velocitypose.angular_velocity = v_angular
        velocitypose.world_x_position = new_x_pos
        velocitypose.world_y_position = new_y_pos
        velocitypose.heading = new_heading
        velocitypose.world_x_velocity = world_x_vel
        velocitypose.world_y_velocity = world_y_vel


        self.current_pose = velocitypose
        self.localisation_last_updated_time = timestamp

        if self.output_function != None:
            self.output_function(velocitypose)

        return 


    def log_localisation(self, print_to_console = False):
        self.telemetry_logger.log(8, self.current_pose)
        string = f"X: {self.current_pose.world_x_position:.2f}, Y: {self.current_pose.world_y_position:.2f}, H: {self.current_pose.heading:.2f}"
        if print_to_console:
            print(string)
            #TODO debug code
            #origin = (0,0)
            #rel_pos = self.get_relative_position_of_point(origin)
            #dist = self.get_distance_to_point(origin)
            #abs_bear = self.get_absolute_bearing_of_point(origin)
            #rel_bear = self.get_relative_bearing_of_point(origin)
            #print(f"Relative position of origin {rel_pos}, distance {dist}, absolute bearing {abs_bear}, relative bearing {rel_bear}")
        #TODO console output?
    
    def reset_localisation(self):
        last_timestamp = self.current_pose.timestamp
        self.current_pose = VelocityPose() #TODO FIX THIS
        self.current_pose.timestamp = last_timestamp
        self.localisation_last_updated_time = last_timestamp
        return

    def transform_LV_to_WV(self, linear_velocity_local, heading = None):
        """Transforms Local Velocity to World Velocity""" #TODO Fix documentation
        if heading == None:
            heading = self.current_pose.heading
        xl = linear_velocity_local[0]
        yl = linear_velocity_local[1]
        xw = xl*cos(heading) - yl*sin(heading)
        yw = xl*sin(heading) + yl*cos(heading)
        return xw, yw
    
    def transform_WV_to_LV(self, linear_velocity_world, heading = None):
        """Transforms World Velocity to Local Velocity""" #TODO Fix documentation
        if heading == None:
            heading = self.current_pose.heading
        xw = linear_velocity_world[0]
        yw = linear_velocity_world[1]
        xl = xw*cos(-heading) - yw*sin(-heading) #TODO this may be wrong, so might the one above
        yl = xw*sin(-heading) + yw*cos(-heading)
        return xl, yl

    def get_distance_to_point(self, point = (0,0)):
        x,y = self.get_relative_position_of_point(point)
        return (x**2+y**2)**0.5

    def get_relative_position_of_point(self, point = (0,0)):
        x = point[0] - self.current_pose.world_x_position
        y = point[1] - self.current_pose.world_y_position
        return (x,y)

    def get_absolute_bearing_of_point(self, point = (0,0)):
        relative_position = self.get_relative_position_of_point(point)
        bearing = atan2(relative_position[1],relative_position[0])
        return bearing
        
    def get_relative_bearing_of_point(self, point = (0,0)):
        """Returns smallest delta angle to target angle"""
        absolute_bearing = self.get_absolute_bearing_of_point(point)
        relative_bearing = self.get_relative_bearing_from_absolute_bearing(absolute_bearing)
        return relative_bearing

    def get_relative_bearing_from_absolute_bearing(self, absolute_bearing):
        """Returns the smallest relative bearing between the robot heading and an absolute bearing"""
        bearing_a =  absolute_bearing - self.current_pose.heading
        if bearing_a<0:
            bearing_b = bearing_a + 2*pi
        else:
            bearing_b = bearing_a - 2*pi
        if abs(bearing_a) < abs(bearing_b):
            return bearing_a
        else:
            return bearing_b

    def convert_angle_to_bearing(self, angle):
        """Converts an angle of over 2PI or less than 0 to a direction from 0 to 2PI"""
        while angle>=2*pi: #TODO inefficent 
            angle = angle-2*pi
        while angle<0:
            angle = angle+2*pi
        return angle

class VelocityPose: 
    timestamp = 0
    local_x_velocity = 0 #Local frame, velocity, X direction
    local_y_velocity = 0 #Local frame, velocity, Y direction
    angular_velocity = 0 #Local frame, velocity, Rotational
    world_x_position = 0 
    world_y_position = 0
    world_x_velocity = 0
    world_y_velocity = 0
    heading = 0 #RADIANS

    def __init__(self):
        pass

    def __str__(self): #TODO maybe not this?
        return f"{self.timestamp}, {self.world_x_position}, {self.world_y_position}, {self.heading}, {self.local_x_velocity}, {self.local_y_velocity}, {self.angular_velocity}"
