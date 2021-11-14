import time, cv2, json
from vision.monocular import Monocular, test_publisher_pixel_coordinate




def main():
    cam = Monocular(test_publisher_pixel_coordinate)
    
    cam.start_loop()
    cam.debug_mode = True
    cam.debug_type = "cont"
    time.sleep(3)
    while True:
        cv2.imshow("Colour Image", cam.debug_frame_output)
        # Press q if you want to end the loop
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.loop_running = False

if __name__ == "__main__":
    main()
