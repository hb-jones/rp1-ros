from code_snippets import Target
from rp1controller import RP1Client
from vision import monocular
ip = "192.168.137.1"
terminal_gain = 5 #TODO make sure to check command is within limit
delay = 0.1

max_dist = 2 #TODO this is the max distance the robot can move from origin during terminal phase
camera = None
coords = (0,0) #Normalised camera coords
updated = False

def update_terminal_target(HLC):
    global coords, updated, terminal_gain, max_dist
    if not updated:
        return
    updated = False
    #Get most recent camera coords, apply gain
    scaled_coords = (coords[0]*terminal_gain,coords[1]*terminal_gain)
    #Get position
    current_pose = HLC.localisation.current_pose
    #Add some amount to pos based on camera coords
    targ_x = current_pose.world_x_position+scaled_coords[0]
    targ_y = current_pose.world_y_position+scaled_coords[1]
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
    target.world_point(targ_x, targ_y)
    HLC.set_target(target)
    #Artificial delay?
    #no
    pass

def update_camera_coords(cam):
    global coords, updated
    coords = cam.norm_coords
    updated = True

def main():
    print()

    print("Starting camera")
    global camera 
    camera = monocular.Monocular(update_camera_coords,"norm_coord")

    print("Starting Server")
    client = RP1Client(ip, custom_function= update_terminal_target)
    #add update terminal target to client somehow

if __name__ == "__main__":
    main()