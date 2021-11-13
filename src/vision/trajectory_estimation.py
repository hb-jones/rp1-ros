import cv2, time
from math import atan
from statistics import mean
from .vision_config import StereoConfig, TrajectoryConfig, BallConfig
import logging
import logging.config
from scipy import stats

logging.config.fileConfig('vision/logging.conf',disable_existing_loggers=False)


class TrajectoryPoint:
    def __init__(self, x, y, z, timestamp):
        self.x = x #X coordinate in m
        self.y = y #Y coordinate in m
        self.z = z #Z coordinate in m
        self.timestamp = timestamp #Timestamp in seconds
    def __str__(self):
        return f"x: {self.x:.2f}, y: {self.y:.2f}, z: {self.z:.2f}, time: {self.timestamp:.2f}s"

def get_target_pixel_position_moment(frame): #TODO need to finish diameter
    """Gets the COM of a target in pixel coordinates"""
    moments = cv2.moments(frame)
    if moments["m00"] == 0:
        return False
    centroid_X = int(moments["m10"] / moments["m00"])
    centroid_Y = int(moments["m01"] / moments["m00"])

    pixel_coordinate = (centroid_X,centroid_Y) #Pixel coordinate of target
    mass = moments["m00"] #Area diameter of target 
    pixel_diameter = 0 #TODO
    return pixel_coordinate, mass, pixel_diameter

def get_displacement_between_points(point_a:TrajectoryPoint , point_b: TrajectoryPoint):
    a = point_a
    b = point_b
    return ((b.x - a.x)**2 + (b.y - a.y)**2 + (b.z - a.z)**2)**0.5       

class Trajectory:
    def __init__(self):
        self.g = -9.81

        self.v_xi = 0 #Initial X velocity
        self.v_yi = 0
        self.v_zi = 0
        self.x_i = 0
        self.y_i = 0
        self.z_i = 0 #initial z coordinate 
        self.t_i = 0 #Timestamp of the initial state

    def get_pos_at_timestamp(self, time): #Relitive to absolute timestamp
        t = time-self.t_i
        return self.get_pos_at_throw_time(t)

    def get_pos_at_throw_time(self, time): #Relative to start of throw
        x = self.v_xi*time+self.x_i
        y = self.v_yi*time+self.y_i
        z = self.v_zi*time+(0.5*self.g)*time**2+self.z_i
        pos = TrajectoryPoint(x,y,z,time)
        return pos

    
    
    def get_ground_intercept(self, relative_time = False): #TODO
        """Returns the ground intercept with the highest timestamp"""
        z=  0
        t_a = (-self.v_zi+(self.v_zi**2-4*self.g*0.5*self.z_i)**0.5)/(2*self.g*0.5)
        t_b = (-self.v_zi-(self.v_zi**2-4*self.g*0.5*self.z_i)**0.5)/(2*self.g*0.5)
        time = max(t_a,t_b)
        x = self.v_xi*time+self.x_i
        y = self.v_yi*time+self.y_i
        if relative_time:
            intercept = TrajectoryPoint(x,y,z,time)
        else:
            intercept = TrajectoryPoint(x,y,z,time+self.t_i)
        return intercept


class TrajectoryEstimator:
    #Static vals
    INVALID = 0
    CALCULATING = 20
    VALID = 10

    def __init__(self):
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        self.config = TrajectoryConfig
        self.positon_array = [] #Array of TrajectoryPoints
        self.trajectory_status = self.INVALID
        self.impact_point:TrajectoryPoint = None #Estimated impact point, timestamp is impact time

    def add_point(self, point:TrajectoryPoint):
        self.positon_array.append(point)
        self.calculate_trajectory()

    def clear_points(self): #TODO check incase additonal variables are added
        self.positon_array.clear()
        self.trajectory_status = self.INVALID
        return True

    def calculate_trajectory(self):#TODO Should be done async
        if not self.check_positions(): #TODO remove false
            self.trajectory_status = self.INVALID
            return False

        #Calculate initial conditions
        vel_x, vel_y, vel_z, x_init, y_init, z_init, t_init = self.get_initial_conditions()

        #Calculate trajectory
        trajectory = Trajectory()
        trajectory.x_i = x_init
        trajectory.y_i = y_init
        trajectory.z_i = z_init
        trajectory.t_i = t_init
        trajectory.v_xi = vel_x
        trajectory.v_yi = vel_y
        trajectory.v_zi = vel_z
        self.trajectory = trajectory
        
        #Extract intercept and set flags
        self.trajectory_status = self.VALID
        #Should log calculation along with current coords in custom log datatype to JSON.
        #Not sure if needed with new trajectory datatype, more useful just to store coords.
        return True

    def get_initial_conditions(self):
        #calculates the angle of the throw using linear interpolation in both axes
        x = []
        y = []
        z = []
        z_lin = []      #Z points with acceleration removed TODO
        g = -9.81        #Gravity
        t = []
        timestart = self.positon_array[0].timestamp
        for points in self.positon_array:
            x.append(points.x)
            y.append(points.y)
            z.append(points.z)
            z_lin.append(points.z-0.5*g*(points.timestamp-timestart)**2)
            t.append(points.timestamp)
    
        vel_x, intercept_vx, r_value_vx, p_value_vx, std_err_vx = stats.linregress(t,x)
        vel_y, intercept_vy, r_value_vy, p_value_vy, std_err_vy = stats.linregress(t,y)
        vel_z, intercept_vy, r_value_vy, p_value_vy, std_err_vy = stats.linregress(t,z_lin) #Normalised vel

        x_i = x[0]#mean(x)
        y_i = y[0]#mean(y)
        z_i = z[0]#mean(z)
        t_i = t[0]#mean(t)

        return vel_x, vel_y, vel_z, x_i, y_i, z_i, t_i

    def get_initial_conditions_poly(self):
        x = []
        y = []
        z = []
        t = []
        
        for points in self.positon_array:
            x.append(points.x)
            y.append(points.y)
            z.append(points.z)
            t.append(points.timestamp)
        



    def check_positions(self):
        #maybe remove certain datapoints if not valid

        #Check count, if too few then return false
        if len(self.positon_array)<self.config.min_datapoints:
            #self.logger.debug(f"trajectory_not_calculated: Needs {self.config.min_datapoints} datapoints, only has {len(self.positon_array)}")
            return False

        #Check difference in times, displacement and velocity
        last:TrajectoryPoint = self.positon_array[0]
        for point in self.positon_array[1:]:
            point:TrajectoryPoint
            time_difference = point.timestamp - last.timestamp
            displacement = get_displacement_between_points(point, last)
            velocity = displacement/time_difference
            if time_difference>self.config.max_time_between_points:
                self.logger.debug(f"trajectory_not_calculated: Time between points too large: {time_difference:.2}s")
                return False
            if displacement>self.config.max_distance_between_points:
                self.logger.debug(f"trajectory_not_calculated: Distance between too large: {displacement:.2}m")
                return False
            if velocity>self.config.max_velocity:
                self.logger.debug(f"trajectory_not_calculated: Velocity too large: {velocity:.2}m/s")
                return False
            last = point

        return True

    def get_impact_point(self, relative_time = False): #TODO should return trajectory point with timestamp representing impact time
        if self.trajectory_status != self.VALID:
            #self.logger.debug(f"impact_point_not_sent: Status is {self.trajectory_status}")
            return False
        return self.trajectory.get_ground_intercept(relative_time)

    def get_last_update_age(self):
        """Returns the time since the last update"""
        return time.time()-self.positon_array[-1].timestamp

    def stereo_publisher(self, stereo): #TODO make sure this works
        """To be passed to stereo cam so that it can update the trajectory"""
        from . import stereo as stereo_module
        #print(f"Stereo publish{stereo.cartesian_coords}")#TODO Debug
        timestamp = stereo.last_update
        coords = stereo.cartesian_coords
        x = coords[0]
        y = coords[1]
        z = coords[2]
        point = TrajectoryPoint(x,y,z,timestamp)
        self.add_point(point)

        stereo_module.test_publisher_pixel_coordinate(stereo) #DEBUG

if __name__ == "__main__":
    import json, time
    filename = "vision/log/90fpsiback.json"
    correct_displacement = "100 Front"
    with open(filename, "r") as file:
            data = json.load(file)
    print(len(data))
    estimator = TrajectoryEstimator()
    initial_time = data[0]["timestamp"]
    for datum in data:
        point = TrajectoryPoint(datum["x"], datum["y"],datum["z"], datum["timestamp"] )
        estimator.add_point(point)
        time.sleep(0.2)
        if estimator.trajectory_status == TrajectoryEstimator.VALID:
            print(f"Expected impact: {estimator.get_impact_point(True)}")
            print(f"Displacement: {get_displacement_between_points(estimator.get_impact_point(True), TrajectoryPoint(0,0,0,0))}")
        else:
            print("INVALID")
        print()
    pass