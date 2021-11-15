import threading, cv2, time
from .monocam import MonoCam
from .vision_config import BallConfig, MonocularConfig 
from . import preprocessing
from .trajectory_estimation import get_target_pixel_position_moment
from vision import monocam

from vision import vision_config


def check_empty(frame):
    """Checks if a frame is empty"""
    gs_masked_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Must be in greyscale colourspace
    moments = cv2.moments(gs_masked_frame)
    if moments["m00"] == 0:
        return True
    else:
        return False    

class Monocular():
    loop_running = False #Flag for main loop

    #Debug/logging stuff
    image_id = 0
    debug_mode = False #If set will save images as they are aquired, TODO add oneshot mode
    debug_currrent = False #set at start of loop if debug mode is on, makes sure an entire set is logged and not a partial
    debug_type = "oneshot" # "onshot" or "cont", determines if debug will auto shut off after one frame

    #Outputs
    last_update = 0 #Time in seconds of the last update
    last_update_type = "pixel_coord"
    pixel_coords = (0,0)
    pixel_diameter = 0
    norm_coords = (0,0)
    distance = 0
    cartesian_coords = (0,0,0)
    trajectory = None


    def __init__(self, publisher_func, mode: str = "norm_coord"): # mode determines if a trajectory is calculated
        self.camera: MonoCam = MonoCam()
        self.publisher_func:function = publisher_func
        self.mode = mode


    def start_loop(self):
        if self.loop_running:
            print(f"Stream already running!")
            return
        self.camera.start_stream() #Start capturing from camera
        self.loop_running = True
        self.main_loop_handle = threading.Thread(target=self.main_loop)
        self.main_loop_handle.start()

    def main_loop(self): #TODO
        while self.loop_running:
            self.image_id += 1
            if self.debug_mode:
                self.debug_currrent = True #Tells image saver that it can start saving images
            raw_frame = self.camera.get_next_image()

            preprocessed_frame = self.preprocess(raw_frame)
            moment_result = get_target_pixel_position_moment(preprocessed_frame)
            if moment_result is False:
                #print(f"Invalid Moment: Image {self.image_id}")
                continue
            
            pixel_coords, mass, pixel_diameter = moment_result
            self.mass = mass
            if mass<MonocularConfig.min_mass:
                continue
            # draw the center and diameter of the circle
            com_frame = cv2.circle(raw_frame,pixel_coords,2,(0,0,255),3)
            com_frame = cv2.circle(com_frame,pixel_coords,int(pixel_diameter/2+20),(255,0,255),3)
            com_frame = cv2.circle(com_frame,(int(len(com_frame[0])/2), int(len(com_frame)/2)),int(pixel_diameter/2+20),(255,0,255),3)
            self.save_image(com_frame, "com_frame")

            
            
            if self.mode == "pixel_coord": #TODO #Publish just this, and maybe distance
                self.last_update_type = self.mode
                self.last_update = time.time()
                self.pixel_coords = pixel_coords
                self.pixel_diameter = pixel_diameter
                self.norm_coords = (0,0)
                self.distance = 0
                self.cartesian_coords = (0,0,0)
                self.trajectory = None

                self.publisher_func(self) #TODO call this after updating self 

            elif self.mode == "norm_coord":
                distance = self.pixel_diameter_to_distance(pixel_diameter)


                self.last_update_type = self.mode
                self.last_update = time.time()
                self.pixel_coords = pixel_coords
                self.pixel_diameter = pixel_diameter
                self.norm_coords = (pixel_coords[0]*2/len(com_frame[0])-1,pixel_coords[1]*2/len(com_frame)-1) #TODO Ensure are correct
                self.distance = 0
                self.cartesian_coords = (0,0,0)
                self.trajectory = None

                self.publisher_func(self)
            
            else:
                cartestian_coord_camera_frame = self.pixel_coord_to_cartesian(pixel_coords, pixel_diameter)
                #TODO work out distance here from coords
                cartestian_coord_world_frame = self.transform_camera_frame_to_world_frame(cartestian_coord_camera_frame)
                #Feed into trajectory sys, will write this when I do the stereo system TODO


                self.last_update_type = self.mode
                self.last_update = time.time()
                self.pixel_coords = pixel_coords
                self.pixel_diameter = pixel_diameter
                self.norm_coords = (0,0)
                self.distance = 0
                self.cartesian_coords = (0,0,0)
                self.trajectory = None

                self.publisher_func(self)

            if self.debug_mode and self.debug_type == "oneshot" and self.debug_currrent:
                    self.debug_mode = False
                    self.debug_currrent  = False
            


    def preprocess(self, raw_frame):

        #print(f"Raw frame empty? {check_empty(raw_frame)}")
        #Save raw image
        self.save_image(raw_frame, "raw_frame")
        
        #Crop frame
        cropped_frame = preprocessing.crop(raw_frame, MonocularConfig.crop_topleft, MonocularConfig.crop_bottomright)
        self.save_image(cropped_frame, "cropped_frame")
        #print(f"crop frame empty? {check_empty(cropped_frame)}")


        #Mask ball
        masked_frame = preprocessing.mask(cropped_frame, MonocularConfig.mask_lower, MonocularConfig.mask_upper)
        self.save_image(masked_frame, "masked_frame")
        #print(f"mask frame empty? {check_empty(masked_frame)}")

        #Remove disconnected masses
        opened_frame = preprocessing.morph_open(masked_frame, MonocularConfig.open_kernal_size)
        self.save_image(opened_frame, "opened_frame")
        #print(f"open frame empty? {check_empty(opened_frame)}")

        #Fill holes in ball
        closed_frame = preprocessing.morph_close(opened_frame, MonocularConfig.close_kernal_size)
        self.save_image(closed_frame, "closed_frame")
        #print(f"closed frame empty? {check_empty(closed_frame)}")

        #Threshold to binary
        thresholded_frame = preprocessing.threshold(closed_frame)
        self.save_image(thresholded_frame, "thresholded_frame")
        #print(f"thresh frame empty? {check_empty(thresholded_frame)}")
        #print()
        #print()
        #time.sleep(0.3) #TODO really need to remove this

        return thresholded_frame

    def pixel_diameter_to_distance(self, pixel_diameter): #TODO basic function to estimate distance, does not account for calibration
        return 1

    def pixel_coord_to_cartesian(self, pixel_coord, pixel_diameter): #TODO
        """Returns the positon of an object in cartesian coordinates relative to the camera frame"""
        return (1,1,1)
    
    def transform_camera_frame_to_world_frame(self, coordinate): #TODO 
        return coordinate

    def record_singe_image_set(self):
        self.debug_type = "oneshot"
        self.debug_mode = True

    def save_image(self, frame, image_name): #TODO async func to save images to a file
        #needs to set filename based on image id at start to ensure it has not been updated.
        if frame is not False and image_name == "thresholded_frame":# "thresholded_frame":

            self.debug_frame_output = frame 
        return

    


def test_publisher_pixel_coordinate(monocular):
    targ = (0,-0.5)
    new_coord = (monocular.norm_coords[0]-targ[0], monocular.norm_coords[1]-targ[1])
    print(new_coord)
    print(monocular.mass)
    print()
    return 

if __name__ == "__main__":
    pass