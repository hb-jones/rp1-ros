from logging import config
import threading, cv2, time, json
from .stereocam import StereoCam
from .vision_config import BallConfig, StereoConfig, MonocularConfig
from . import preprocessing, trajectory_estimation, monocular

class Stereo(monocular.Monocular):


    def __init__(self, publisher_func, mode: str = "all", trajectory = None): # mode determines if a trajectory is calculated
        self.camera: StereoCam = StereoCam(StereoCam.set_depth_rs_config())
        self.publisher_func:function = publisher_func
        self.mode = mode
        self.trajectory = trajectory

    def main_loop(self): #TODO
        while self.loop_running:
            self.image_id += 1
            if self.debug_mode:
                self.debug_currrent = True #Tells image saver that it can start saving images

            raw_frame, timestamp = self.camera.get_next_depth_image()


            preprocessed_frame = self.preprocess(raw_frame)

            moment_result = trajectory_estimation.get_target_pixel_position_moment(preprocessed_frame)
            if moment_result is False:
                #print(f"Invalid Moment: Image {self.image_id}") #Fires if image has no ball
                continue
            
            pixel_coords, mass, pixel_diameter = moment_result
           
            if mass<StereoConfig.min_mass:
                #print(f"Mass {mass}") #Fires if image is too small
                continue
            #TODO this should remove incomplete detections
            if not (preprocessed_frame[pixel_coords[1],-1] == 0 and preprocessed_frame[pixel_coords[1],0] == 0 and preprocessed_frame[0,pixel_coords[0]] == 0 and preprocessed_frame[-1,pixel_coords[0]] == 0):
                print("Incomplete Ball")
                continue
            #print(pixel_coords)
            # draw the center and diameter of the circle
            com_frame = cv2.applyColorMap(cv2.convertScaleAbs(raw_frame, alpha=0.03), cv2.COLORMAP_JET)
            com_frame = cv2.circle(com_frame,pixel_coords,2,(0,0,255),3)
            com_frame = cv2.circle(com_frame,pixel_coords,int(pixel_diameter/2),(0,0,255),3)
            self.save_image(com_frame, "com_frame")

            
            
            if self.mode == "all": #TODO 
                distance = raw_frame[pixel_coords[1]][pixel_coords[0]]+BallConfig.ball_diameter*1000/2


                cartestian_coord_camera_frame = self.camera.get_coord_of_depth_frame_pixel(pixel_coords, distance)
                cartestian_coord_world_frame = self.transform_camera_frame_to_world_frame(cartestian_coord_camera_frame)



                self.last_update_type = self.mode
                self.last_update = time.time()
                self.pixel_coords = pixel_coords
                self.pixel_diameter = pixel_diameter
                self.norm_coords = (0,0)
                self.distance = distance
                self.cartesian_coords = cartestian_coord_world_frame

                coords = cartestian_coord_world_frame
                self.coord = {"x":coords[0],"y":coords[1],"z":coords[2], "timestamp":timestamp}

                

                #print(self.distance) #TODO DEBUG

            self.publisher_func(self) #TODO call this after updating self 

            if self.debug_mode and self.debug_type == "oneshot":
                    self.debug_mode = False
                    self.debug_currrent  = False
        self.camera.stop_stream()

    def preprocess(self, raw_frame):
        #Save raw image
        self.save_image(raw_frame, "raw_frame")
        
        #Crop frame
        cropped_frame = preprocessing.crop(raw_frame, StereoConfig.crop_topleft, StereoConfig.crop_bottomright)
        self.save_image(cropped_frame, "cropped_frame")

        #Distance crop
        distance_cropped_frame = preprocessing.distance_crop(cropped_frame, StereoConfig.dist_crop_min, StereoConfig.dist_crop_max)
        self.save_image(distance_cropped_frame, "distance_cropped_frame")

        #Remove disconnected masses
        opened_frame = preprocessing.morph_open(distance_cropped_frame, StereoConfig.open_kernal_size)
        self.save_image(opened_frame, "opened_frame")

        #Fill holes in ball
        closed_frame = preprocessing.morph_close(opened_frame, StereoConfig.close_kernal_size)
        self.save_image(closed_frame, "closed_frame")

        #Threshold to binary
        thresholded_frame = preprocessing.stereo_threshold(closed_frame)
        self.save_image(thresholded_frame, "thresholded_frame")

        return thresholded_frame

    
    def transform_camera_frame_to_world_frame(self, coordinate): #TODO 
        #RS local axes are defined with X right, Y down, Z towards facing direction.
        #These need to be converted to the same axes as robot platform uses.
        #X forward, Y left (TODO check positive value is left) and Z up
        x_l = coordinate[2]/1000 #z_rs becomes x
        y_l = -coordinate[0]/1000 #-x_rs becomes y
        z_l = -coordinate[1]/1000 #-y_rs becomes z

        rotaton_matrix = StereoConfig.rotation_matrix

        x_rotated = x_l*rotaton_matrix[0][0]+y_l*rotaton_matrix[1][0]+z_l*rotaton_matrix[2][0]
        y_rotated = x_l*rotaton_matrix[0][1]+y_l*rotaton_matrix[1][1]+z_l*rotaton_matrix[2][1]
        z_rotated = x_l*rotaton_matrix[0][2]+y_l*rotaton_matrix[1][2]+z_l*rotaton_matrix[2][2]

        x_translated = x_rotated-StereoConfig.camera_position[0]
        y_translated = y_rotated-StereoConfig.camera_position[1]
        z_translated = z_rotated-StereoConfig.camera_position[2]

        world_coord = [x_translated, y_translated, z_translated]

        #print(f"Coord: {[x_l, y_l, z_l]}, {world_coord:}")

        #print(f"{x_translated:3f},{y_translated:3f},{z_translated:3f}")

        return world_coord

    def record_singe_image_set(self):
        self.debug_type = "oneshot"
        self.debug_mode = True

    def save_image(self, frame, image_name): #TODO async func to save images to a file
        #needs to set filename based on image id at start to ensure it has not been updated. 
        if frame is not False and image_name == "thresholded_frame":

            self.debug_frame_output = frame
        return

def test_publisher_pixel_coordinate(stereo: Stereo):
    """Test file that saves coords to a json file for testing with traj predictor"""
    filename = "vision/log/coords.json"
    if stereo.coord is not None:
        with open(filename, "r+") as file:
            try:
                data = json.load(file)
            except:
                data = []
            data.append(stereo.coord)
            file.seek(0)
            json.dump(data, file)
    return 

if __name__ == "__main__":
    stereo = Stereo(test_publisher_pixel_coordinate)
    stereo.debug_mode = True
    stereo.debug_type = "cont"
    stereo.start_loop()
    time.sleep(2)
    while True:
        cv2.imshow("Colour Image", stereo.debug_frame_output)
        # Press q if you want to end the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stereo.loop_running = False
