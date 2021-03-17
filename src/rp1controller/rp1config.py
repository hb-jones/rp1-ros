
from typing import Dict

class WheelTransform:
        def __init__ (self, x_translate_sign, y_translate_sign, angular_sign):
            self.x_translate_sign = x_translate_sign #Half the distance between wheel centres in x direction in metres
            self.y_translate_sign = y_translate_sign
            self.angular_sign = angular_sign

class KinematicModel(): #may have additional ROS functionality or be replaced entirely with a TF based system
    """Based on Kinematic Model of a Four Mecanum Wheeled Mobile Robot, H. Taheri, B. Qiao, N. Ghaeminezhad
    at       https://research.ijcaonline.org/volume113/number3/pxc3901586.pdf
    but also https://onlinelibrary.wiley.com/doi/full/10.1002/zamm.201900173
    #TODO X is forward for the robot
    """
    wheel_radius = 0.098/2 #Radius in metres 
    wheel_pos_x = 0.276/2 #Half the distance between wheel centres in x direction in metres
    wheel_pos_y = 0.400/2 #TODO x and y may need to be flipped as X is forward

    gear_ratio = 15/80 #TODO

    wheel_transforms = {}
    motor_transforms = {}

    
    def __init__(self, config):
        self.config = config
        self.wheel_transforms.update({"axis_FL": WheelTransform(1, -1, -1)})
        self.wheel_transforms.update({"axis_FR": WheelTransform(1,  1,  1)})
        self.wheel_transforms.update({"axis_BL": WheelTransform(1,  1, -1)})
        self.wheel_transforms.update({"axis_BR": WheelTransform(1, -1,  1)})

        self.motor_transforms.update({"axis_FL":  1})
        self.motor_transforms.update({"axis_FR": -1})
        self.motor_transforms.update({"axis_BL":  1})
        self.motor_transforms.update({"axis_BR": -1})
        return

    def transform_velocity_base_to_motor(self, linear_x, linear_y, angular):
        vel_wheels = self.transform_velocity_base_to_wheel(linear_x, linear_y, angular)
        vel_motors = self.transform_velocity_wheel_to_motor(vel_wheels)
        return vel_motors

    def transform_velocity_motor_to_base(self, motor_velocities):
        vel_wheels = self.transform_velocity_motor_to_wheel(motor_velocities)
        linear_x, linear_y, angular = self.transform_velocity_wheel_to_base(vel_wheels)
        return linear_x, linear_y, angular


    def transform_velocity_base_to_wheel(self, linear_x, linear_y, angular):
        """Returns target speeds for each wheel. Inputs in m/s, m/s and rad/s, outputs are in rad/s"""
        wheel_targets = {}
        for wheel_name in self.wheel_transforms:
            wheel: WheelTransform = self.wheel_transforms[wheel_name]
            target = 1/self.wheel_radius*(wheel.x_translate_sign*linear_x+wheel.y_translate_sign*linear_y+wheel.angular_sign*angular*(self.wheel_pos_x+self.wheel_pos_y))
            wheel_targets.update({wheel_name: target})
        return wheel_targets

    def transform_velocity_wheel_to_base(self, wheel_velocities: Dict): 
        """Takes dictionary of wheel speeds in rads/s and returns linear x, linear y, and angular in rads/s"""
        vx_unscaled = 0
        vy_unscaled = 0
        vang_unscaled = 0
        for wheel_name in wheel_velocities:
            wheel_vel = wheel_velocities[wheel_name]
            vx_unscaled = vx_unscaled + (wheel_vel*self.wheel_transforms[wheel_name].x_translate_sign)
            vy_unscaled = vy_unscaled + (wheel_vel*self.wheel_transforms[wheel_name].y_translate_sign)
            vang_unscaled = vang_unscaled + (wheel_vel*self.wheel_transforms[wheel_name].angular_sign)
        vx = vx_unscaled*self.wheel_radius/4
        vy = vy_unscaled*self.wheel_radius/4
        vang = vang_unscaled*self.wheel_radius/(4*(self.wheel_pos_x+self.wheel_pos_y))
        return vx, vy, vang

    def transform_velocity_wheel_to_motor(self, wheel_velocities): #TODO probably just include these in velocity_base_to_motor()
        """In rad/s"""
        motor_velocities = {}
        for wheel_name in wheel_velocities:
            wheel_vel = wheel_velocities[wheel_name]
            motor_vel = wheel_vel*self.motor_transforms[wheel_name]*1/self.gear_ratio
            motor_velocities.update({wheel_name: motor_vel})        
        return motor_velocities

    def transform_velocity_motor_to_wheel(self, motor_velocities):
        """In rad/s""" 
        wheel_velocities = {}
        for wheel_name in motor_velocities:
            motor_vel = motor_velocities[wheel_name]
            wheel_vel = motor_vel*self.motor_transforms[wheel_name]*self.gear_ratio
            wheel_velocities.update({wheel_name: wheel_vel})        
        return wheel_velocities


class RP1Configuration(): 
    odrvF_serial_number = "208239904D4D" #String containing front ODrive's serial number in hex format all capitals
    odrvB_serial_number = "206039994D4D" #String containing back  ODrive's serial number in hex format all capitals
    model = None #The kinematic model containing robot size, gear ratio etc

    pos_gain = 12
    vel_gain = 0.004
    vel_integrator_gain = 0.021
    vel_ramp_rate = 100

    acceleration_max = 0.2 #m/s^2 #TODO implement
    linear_velocity_max = 1 #m/s
    angular_velocity_max = 1 #rad/s

    safe_linear_velocity = 0.5
    safe_angular_velocity = 0.6

    linear_velocity_stable_min = 0.2 #TODO Adjust #Minimum speed robot can move and keep stable
    angular_velocity_stable_min = 0.2

    max_error_position = 0.1
    max_error_velocity = 0.1
    max_error_bearing = 0.1

    def __init__(self):
        self.model = KinematicModel(self) #The kinematic model containing robot size, gear ratio etc
