import numpy as np

class BallConfig:
    ball_diameter = 0.1 #Diameter in m
    ball_colour = None #TODO


class MonocularConfig:
    crop_topleft = (0,0)
    crop_bottomright = (0,0)

    mask_lower = np.array([22,0,0])
    mask_upper = np.array([31,255,170])

    open_kernal_size = 9
    close_kernal_size = 40

    pass #Camera calibration etc


class StereoConfig:

    crop_topleft = (0,0)
    crop_bottomright = (0,0)#(100,675)
    dist_crop_min = 200
    dist_crop_max = 700#1500

    open_kernal_size = 7
    close_kernal_size = 11

    min_mass =  1000000


    #negative of position in world in m, world defined as robot's starting location at ground level
    #X forward, Y left, Z up
    camera_position = [-2.2,0.5,-0.79] #TODO Might need to invert a couple
    
    
    x_id = [0,1,0]
    y_id = [-1/(2**0.5),0,1/(2**0.5)]
    z_id = [1/(2**0.5),0,1/(2**0.5)]
    rotation_matrix = [x_id, y_id, z_id]

    def __init__(self):
        pass


class TrajectoryConfig:
    #Coordinates check
    min_datapoints = 3   #Number of needed datapoints to estimate trajectory
    max_velocity = 20 #Metres per second
    max_distance_between_points = 1 #Metres, will need to increase to 30 if estimating at both ends
    max_time_between_points = 5 #seconds

    #Drag calculations, if needed
    kinematic_viscosity = 1.81 *10**-5 #At 15C


    #Finished Trajectory Check
    