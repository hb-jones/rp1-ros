#!/usr/bin/env python
import pyrealsense2 as rs
import numpy as np
import cv2
import threading

class StereoCam():
    paused = True
    depth_flag = False
    colour_flag = False
    pc_flag = False
    colour_frame = None
    depth_frame = None
    points_frame = None

    def __init__(self, config = None, pointcloud = False):
        """Simple wrapper that may be replaced with advanced mode"""
        #Initialise general settings and variables
        self.pipeline = rs.pipeline()
        if config is not None:
            self.config = config
        else:
            self.config = StereoCam.set_default_rs_config()
        self.profile = self.pipeline.start(self.config)
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_profile = rs.video_stream_profile(self.profile.get_stream(rs.stream.depth))
        self.depth_intrinsics = depth_profile.get_intrinsics()
        self.depth_scale = depth_sensor.get_depth_scale()
        self.generate_pointcloud = pointcloud
        self.pointcloud_frame = rs.pointcloud()
        self.depthUnitTransform = rs.units_transform()
        

    def __del__(self):
        """Gracefully exit"""
        if self.streamThread is not None:
            self.paused = True
            self.streamThread.join()
        self.pipeline.stop()

    def set_default_rs_config():
        """Sets the default config"""
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        return config

    def set_depth_rs_config():
        """90fps depth stream"""
        config = rs.config()
        config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)
        return config

    def set_high_speed_rs_config():
        """300fps depth Stream"""
        config = rs.config()
        config.enable_stream(rs.stream.depth, 848, 100, rs.format.z16, 300)
        return config
    
    def start_stream(self):
        """Start streams"""
        self.paused = False
        self.streamThread = threading.Thread(target = self.__stream)
        self.streamThread.start()

    def stop_stream(self):
        self.paused = True
        if self.streamThread is not None:
            self.streamThread.join()
        
    def __stream(self):
        while not self.paused:
            frames = self.pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if depth_frame and color_frame and self.generate_pointcloud:
                self.build_point_cloud(depth_frame,color_frame)

            elif depth_frame and self.generate_pointcloud:
                self.build_point_cloud(depth_frame)
            if depth_frame: #Fix frame checking
                self.depth_flag = True
                self.depth_frame = depth_frame
                
            if color_frame:
                self.colour_frame = color_frame
                self.colour_flag = True
            
    
    def build_point_cloud(self, depth, color = False):
        points = self.pointcloud_frame.calculate(depth)
        color = False #TODO Fix
        if color:
            self.pointcloud_frame.map_to(color)
        else:
            self.pointcloud_frame.map_to(depth)
        self.points_frame = points
        self.pc_flag = True


    def get_next_image(self): 
        rs_frame = self.get_colour_frame()
        while not rs_frame:
            rs_frame = self.get_colour_frame()
        image = np.asanyarray(rs_frame.get_data())
        return image
    
    def get_next_depth_image(self): 
        rs_depth = self.get_depth_frame()
        
        while not rs_depth:
           rs_depth = self.get_depth_frame() 
        depth_image = np.asanyarray(rs_depth.get_data())
        return depth_image, rs_depth.get_timestamp()/1000 #Converts timestamp from miliseconds to seconds

    def depth_frame_to_colourmap(self, depth_image):
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        return depth_colormap

    def get_coord_of_depth_frame_pixel(self, pixel_coordinates, distance):
        """Returns XYZ coord, X is right, Y is down, Z is dir camera is facing"""
        return rs.rs2_deproject_pixel_to_point(self.depth_intrinsics, pixel_coordinates, distance)

    def get_colour_frame(self):
        if self.colour_flag:
            self.colour_flag = False
            return self.colour_frame
        else:
            return False

    def get_depth_frame(self):
        if self.depth_flag:
            self.depth_flag = False
            return self.depth_frame
        else:
            return False

    def get_point_cloud(self):
        if self.pc_flag:
            self.pc_flag = False
            return self.points_frame
        else:
            return False


if __name__ == "__main__":
    from time import sleep
    import time
    cam = StereoCam()
    cam.start_stream()
    while True:
        frame = cam.get_next_image()
        depth_frame, timestamp = cam.get_next_depth_image()
        if frame is not False:
            cv2.imshow("Colour Image", frame)
        if depth_frame is not False:
            cv2.imshow("Depth Image", cam.depth_frame_to_colourmap(depth_frame))
            
            
            #TEsting to check if distance can be easily found, also check git
            
            print(f"Distance centre: {depth_frame[int(480/2)][int(640/2)]/1000}m")
            print(f"Time RS: {timestamp}")
            print(f"Time PY: {time.time()}")
            sleep(0.5)




        # Press q if you want to end the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stop_stream()