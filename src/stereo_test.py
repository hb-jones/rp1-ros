import json, cv2, time
from vision.stereo import Stereo

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
