import numpy as np

class BallConfig:
    ball_diameter = 0.1 #Diameter in m
    ball_colour = None #TODO


class MonocularConfig:
    crop_topleft = (0,70)
    crop_bottomright = (int(1200/2-0),int(1600/2-70))

    mask_lower = np.array([20,200,0])
    mask_upper = np.array([35,255,255])

    open_kernal_size = 9
    close_kernal_size = 40

    min_mass = 30000 #SMallest size of a return to be a ball

    pass #Camera calibration etc


class StereoConfig:

    crop_topleft = (0,0)
    crop_bottomright = (480,700)#(400,680)#(100,675)
    dist_crop_min = 200
    dist_crop_max = 1400

    open_kernal_size = 7
    close_kernal_size = 11

    min_mass =  1000000


    #negative of position in world in m, world defined as robot's starting location at ground level
    #X forward, Y left, Z up
    #camera_position = [-4.55,0.32,-1.38+0.230+0.09] #0.2 is height of robot, may need to add bin height
    camera_position = [-4.46,0.32,-1.375+0.52]
    


    x_id = [0,1,0]
    y_id = [-1/(2**0.5),0,1/(2**0.5)]
    z_id = [1/(2**0.5),0,1/(2**0.5)]
    rotation_matrix = [x_id, y_id, z_id]

    def __init__(self):
        pass


class TrajectoryConfig:
    #Coordinates check
    min_datapoints = 4   #Number of needed datapoints to estimate trajectory
    max_velocity = 20 #Metres per second
    max_distance_between_points = 1 #Metres, will need to increase to 30 if estimating at both ends
    max_time_between_points = 5 #seconds

    #Drag calculations, if needed
    kinematic_viscosity = 1.81 *10**-5 #At 15C


    #Finished Trajectory Check
    