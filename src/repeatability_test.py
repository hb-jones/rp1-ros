import time
import rp1_test_server as rp1
import threading
import time
from rp1controller import Target
accelerations = [0.5, 1, 2, 3, 4, 5] #Accelerations to test in m/s^2
positions = [(0.5,0),(0.5,-0.5),(0,0)] #Coordinates of test positions, measurements are taken at final position



weight = 8.5 #kg, for logging

def server_thread():
    rp1.main()

def check_at_pos(position, pose):
    if abs(pose.local_x_velocity) > 0.1 or abs(pose.local_y_velocity) > 0.1:
        return False
    if (abs(pose.world_x_position) - abs(position[0])) < 0.2:
        if (abs(pose.world_y_position) - abs(position[1])) < 0.2:
            return True
    return False



def repeatability_test():
    server = threading.Thread(target=server_thread)
    server.start()
    time.sleep(10)
    rp1.change_mode("pose")
    #Set speed and accel
    time.sleep(0.2)
    for position in positions:
        target = Target()
        target.world_bearing = 0
        target.world_point = position
        rp1.send_target(target)
        time.sleep(0.5)
        pose = rp1.get_odom()
        while not check_at_pos(position, pose):
            print(f"Velocity X{pose.local_x_velocity}, Y{pose.local_y_velocity}")
            time.sleep(0.5)
            pose = rp1.get_odom()
        time.sleep(1)
        print(f"At position {position}")

        

    return








if __name__ == "__main__":
    repeatability_test()