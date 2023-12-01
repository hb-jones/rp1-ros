from threading import active_count
from rp1controller import RP1Client, Target
from vision import monocular
import time
ip = "192.168.43.237"
terminal_gain_x = 10
terminal_gain_y = -5
target_point = (0,-0.8)
delay = 0.1

max_dist = 1.4 #TODO this is the max distance the robot can move from origin during terminal phase
camera = None
coords = (0,0) #Normalised camera coords
updated = False
active = False

def enable_pitbull(var):
    global active
    active = 10

def update_terminal_target(HLC):
    global active, coords, updated, terminal_gain_x, terminal_gain_y, max_dist, target_point, delay, timestart
    if not updated:
        return
    updated = False

    if active<=0:
        return
    active -=1
    print(f"Target updated: {time.time()}")
    updated_coords = (coords[0]-target_point[0], coords[1]-target_point[1])
    #Get most recent camera coords, apply gain
    scaled_coords = (updated_coords[0]*terminal_gain_y, updated_coords[1]*terminal_gain_x)
    #Get position
    current_pose = HLC.localisation.current_pose
    #Add some amount to pos based on camera coords
    targ_x = current_pose.world_x_position+scaled_coords[1]
    targ_y = current_pose.world_y_position+scaled_coords[0]
    #Make sure is still in allowed area
    if targ_x > max_dist:
        targ_x = max_dist
    elif targ_x < -max_dist:
        targ_x = -max_dist
    if targ_y > max_dist:
        targ_y = max_dist
    elif targ_y < -max_dist:
        targ_y = -max_dist
    #Move to
    target = Target()
    target.world_point = (targ_x, targ_y)
    HLC.set_target(target)
    print(f"Time taken: {time.perf_counter() - timestart}s")
    timestart = time.perf_counter()
    #Artificial delay?
    #no
    return

def update_camera_coords(cam):
    global coords, updated
    print(f"Cam updated: {time.time()}")
    coords = cam.norm_coords
    updated = True

def main():
    global timestart
    timestart = time.perf_counter()
    print()

    print("Starting camera")
    global camera 
    camera = monocular.Monocular(update_camera_coords,"norm_coord")
    camera.start_loop()
    print("Starting Server")
    #client = RP1Client(ip, custom_function= update_terminal_target)
    #add update terminal target to client somehow



    client = RP1Client(ip, custom_function= enable_pitbull)
    time.sleep(5)
    while True:
        update_terminal_target(client.HLC)
        time.sleep(0.01)

if __name__ == "__main__":
    main()
