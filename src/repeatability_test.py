from rp1controller.odometry_system import VelocityPose
import time
import rp1_test_server as rp1
import threading, csv
from rp1controller import Target
from rs_localisation import RSLocalisation
accelerations = [0.5, 1, 2, 3] #Accelerations to test in m/s^2
positions = [(1,0),(1,-0.5),(0,0)] #Coordinates of test positions, measurements are taken at final position
speed_max = 1 #m/s
repeats = 20
mass = 9000 #g, for logging
mechanical_configuration = "single_wheel"

filename = f"test_data/repeatability_{mechanical_configuration}_{mass}g.csv"
def server_thread():
    rp1.main()

def check_at_pos(position, pose):
    if pose == False:
        print("Invalid pose from RP1")
        return False
    if abs(pose.local_x_velocity) > 0.01 or abs(pose.local_y_velocity) > 0.01:
        return False
    if abs(pose.world_x_position - position[0]) < 0.2:
        if abs(pose.world_y_position - position[1]) < 0.2:
            print(f"At position ({pose.world_x_position},{pose.world_y_position})")
            return True
    return False

def get_realsense_estimate(rs, true_position = False):
    rs_pose = rs.get_robot_position(true_position)
    if rs_pose is False:
        rs_pose = rs.get_robot_position(true_position)
        print("RS pose failed")
        time.sleep(0.5)
    return rs_pose


def log_setup():
    with open(filename, 'a', newline='') as csvfile:
        result_logger = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        result_logger.writerow(["mass(g)", "repeat", "acceleration_limit", "x_loc", "y_loc", "x_rs", "y_rs", "d_loc", "d_rs", "error"])
    return

def log_result(mass, repeat, acceleration, rp1_x, rp1_y, rs_x, rs_y):
    with open(filename, 'a', newline='') as csvfile:
        result_logger = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        d_loc = (rp1_x**2+rp1_y**2)**0.5
        d_rs = (rs_x**2+rs_y**2)**0.5

        err = abs(d_loc-d_rs)
        print(f"Displacement: {(err*1000):.1f}mm")
        result_logger.writerow([mass, repeat, acceleration, rp1_x, rp1_y, rs_x, rs_y, d_loc, d_rs, err])

    
    return

def log_result_test(test):
    print(test)
    print()
    return

def displacement(coord):
    return (coord[0]**2 + coord[1]**2)**0.5


def repeatability_test():
    log_setup()
    server = threading.Thread(target=server_thread)
    server.start()
    rs = RSLocalisation()
    time.sleep(1)
    rs_pose = get_realsense_estimate(rs)
    rs.update_robot_origin()

    time.sleep(10)
    rp1.change_mode("pose")
    time.sleep(1)
    rp1.set_config_speed(speed_max)
    time.sleep(1)
    for acceleration in accelerations:
        rp1.set_config_accel(acceleration)
        time.sleep(0.1)
        rp1.set_config_accel(acceleration)
        time.sleep(1)

        for repeat in range(repeats):
            rp1.reset_odometry()
            time.sleep(1.5)
            for position in positions:
                print(f"moving to pos: {position}")
                target = Target()
                target.world_bearing = 0
                target.world_point = position
                rp1.send_target(target)
                time.sleep(0.5)
                pose = rp1.get_odom()
                while not check_at_pos(position, pose):
                    #if pose!= False:
                        #print(f"Velocity X{pose.local_x_velocity}, Y{pose.local_y_velocity}")
                    time.sleep(0.5)
                    pose = rp1.get_odom()
            time.sleep(1)
            localisation_pose = rp1.get_odom()
            while localisation_pose == False:
                localisation_pose = rp1.get_odom()
            rs_pose = get_realsense_estimate(rs)
            
            #log_result_test(f"A: {acceleration}, RP1: {[localisation_pose.world_x_position, localisation_pose.world_y_position]}, RS: {rs_pose}")
            log_result(mass, repeat, acceleration,  localisation_pose.world_x_position, localisation_pose.world_y_position, rs_pose[0], rs_pose[1] )
            
            actual_pos = get_realsense_estimate(rs, true_position=True)
            if displacement(actual_pos)>0.3:
                print(f"Attempting to re centre, displacement: {displacement(actual_pos):.2f}m, pos: ({actual_pos[0]:.2f},{actual_pos[1]:.2f})")
                centre_pos =  (-actual_pos[0], -actual_pos[1])
                print(f"Target pos: {centre_pos[0]:.2f}{centre_pos[1]:.2f}")
                target = Target()
                target.world_bearing = 0
                target.world_point = centre_pos
                rp1.send_target(target)
                time.sleep(2)

                pose = rp1.get_odom()
                while not check_at_pos(centre_pos, pose):
                    time.sleep(1)
                    pose = rp1.get_odom()
            
            rs.update_robot_origin()
    return








if __name__ == "__main__":
    repeatability_test()