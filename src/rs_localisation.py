import pyrealsense2 as rs
import numpy as np
import cv2

class RSLocalisation():
    origin = [0,0] 

    threshold_m00 = 140000



    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)


        depth_profile = rs.video_stream_profile(pipeline_profile.get_stream(rs.stream.depth))
        self.depth_intrinsics = depth_profile.get_intrinsics()

        self.profile = self.pipeline.start(config)
        pass

    def __del__(self):
        print("Closing RS pipeline")
        self.pipeline.stop()

    def get_robot_position(self, true_position = False):
        frames = self.get_frames()
        colour_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        pixel_coordinate, valid = self.get_pixel_coordinate(colour_frame)
        if not valid:
            print("Robot not found")
            return False
        
        depth_at_pixel = depth_frame.get_distance(pixel_coordinate[0], pixel_coordinate[1]) #distance to pixel in m
        coordinate_camera_frame = rs.rs2_deproject_pixel_to_point(self.depth_intrinsics, pixel_coordinate, depth_at_pixel)
        if true_position:
            coordinate_robot_frame = self.convert_to_robot_frame(coordinate_camera_frame, true_position = True)
        else:
            coordinate_robot_frame = self.convert_to_robot_frame(coordinate_camera_frame)
        return coordinate_robot_frame
    
    def get_frames(self):
        align_to = rs.stream.depth
        align = rs.align(align_to)

        frames = self.pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        
        return aligned_frames
    
    def get_colour_image(self):
        frames = self.get_frames()
        colour_frame = frames.get_color_frame()
        colour_image = np.asanyarray(colour_frame.get_data())
        return colour_image

    def get_pixel_coordinate(self, colour_frame):
        lower_colour = np.array([90,200,150])
        upper_colour = np.array([110,255,255])
        
        colour_image = np.asanyarray(colour_frame.get_data())
        hsv_frame = cv2.cvtColor(colour_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_colour, upper_colour)
        
        
        #ret,thresh = cv2.threshold(masked_frame,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        moments = cv2.moments(mask)
        #print(moments["m00"])
        if moments["m00"] < self.threshold_m00:
            return [0,0], False
        centroid_X = int(moments["m10"] / moments["m00"])
        centroid_Y = int(moments["m01"] / moments["m00"])
        


        #Calibration code
        # masked_frame = cv2.bitwise_and(colour_image,colour_image, mask= mask)
        # cv2.circle(masked_frame,(300,300),2,(0,0,255),3)
        # cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
        # cv2.imshow('Test', masked_frame)
        # hsv_val = hsv_frame[300,300]
        # print(f"HSV at point: {hsv_val}")

        return [centroid_X,centroid_Y], True

    def convert_to_robot_frame(self, coord, true_position = False):
        #Realsense should face ground with "Up" towards robots X axis (forwards)
        xa = -coord[1]
        ya = -coord[0]
        if true_position:
            return [xa, ya]
        x = xa - self.origin[0]
        y = ya - self.origin[1]
        print(f"Xc: {coord[0]:.2f}, Yc: {coord[1]:.2f}, Zc: {coord[2]:.2f},           Xr: {x:.2f}, Yr: {y:.2f}")
        return [x,y]
    
    def update_robot_origin(self):
        self.origin = [0,0]
        updated_origin = self.get_robot_position()
        while updated_origin is False:
            updated_origin = self.get_robot_position()
        self.origin = updated_origin
        return

    def get_pixel_coordinate_display(self):
        frames = self.get_frames()
        colour_frame = frames.get_color_frame()
        coord, valid = self.get_pixel_coordinate(colour_frame)
        if not valid:
            return False
        colour_image = np.asanyarray(colour_frame.get_data())
        cv2.circle(colour_image,(coord[0],coord[1]),2,(0,0,255),3)
        #print(coord)
        return colour_image

    

running_flag_test = True
def reset_test(rsloc: RSLocalisation):
    import time
    time.sleep(10)
    while running_flag_test:
        rsloc.update_robot_origin()
        time.sleep(10)
    return



if __name__ == "__main__":
    rsloc = RSLocalisation()
    import threading
    reset_thread = threading.Thread(target=reset_test, args=[rsloc], daemon=True)
    reset_thread.start()
    while True:
        rsloc.get_robot_position()
        images = rsloc.get_pixel_coordinate_display()
        if images is False:
            continue
        
        cv2.namedWindow('Aligned Colour with Object', cv2.WINDOW_NORMAL)
        cv2.imshow('Aligned Colour with Object', images)
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break