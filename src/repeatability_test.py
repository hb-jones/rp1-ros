from rp1controller.odometry_system import VelocityPose
import time
import rp1_test_server as rp1
import threading, csv
from rp1controller import Target
from rs_localisation import RSLocalisation
accelerations = [0.5, 1] #Accelerations to test in m/s^2
positions = [(0.5,0),(0.5,-0.5),(0,0)] #Coordinates of test positions, measurements are taken at final position
speed_max = 2 #m/s
repeats = 2
mass = 8500 #g, for logging
mechanical_configuration = "single_wheel"

filename = f"test_data/repeatability_{mechanical_configuration}_{mass}g.csv"
def server_thread():
    rp1.main()

def check_at_pos(position, pose):
    if pose == False:
        print("Invalid Pose")
        return False
    if abs(pose.local_x_velocity) > 0.02 or abs(pose.local_y_velocity) > 0.02:
        return False
    if (abs(pose.world_x_position) - abs(position[0])) < 0.2:
        if (abs(pose.world_y_position) - abs(position[1])) < 0.2:
            return True
    return False

def get_realsense_estimate(rs):
    rs_pose = rs.get_robot_position()
    if rs_pose is False:
        rs_pose = rs.get_robot_position()
        print("Pose failed")
        time.sleep(0.5)
    return rs_pose


def log_setup():
    with open(filename, 'a', newline='') as csvfile:
        result_logger = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        result_logger.writerow(["mass(g)", "repeat", "acceleration_limit", "x_loc", "y_loc", "x_rs", "y_rs"])
    return

def log_result(mass, repeat, acceleration, rp1_x, rp1_y, rs_x, rs_y):
    with open(filename, 'a', newline='') as csvfile:
        result_logger = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        result_logger.writerow([mass, repeat, acceleration, rp1_x, rp1_y, rs_x, rs_y])

    
    return

def log_result_test(test):
    print(test)
    print()
    return

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
    rp1.set_config_speed(speed_max)
    time.sleep(0.5)
    for acceleration in accelerations:
        rp1.set_config_accel(acceleration)
        time.sleep(0.5)

        for repeat in range(repeats):
            rp1.reset_odometry()
            time.sleep(1)
            for position in positions:
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
            rs.update_robot_origin()
            log_result_test(f"A: {acceleration}, RP1: {[localisation_pose.world_x_position, localisation_pose.world_y_position]}, RS: {rs_pose}")
            log_result(mass, repeat, acceleration,  localisation_pose.world_x_position, localisation_pose.world_y_position, rs_pose[0], rs_pose[1] )

    return








if __name__ == "__main__":
    repeatability_test()