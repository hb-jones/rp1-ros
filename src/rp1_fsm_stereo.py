import rp1_fsm, time, cv2


class RP1_StereoFSM(rp1_fsm.RP1_FSM):
    limit_update_age = 2
    def pitbull(self):
        if time.time()-self.pitbull_time>self.limit_pitbull_age:
            self.disarm = True
            self.logger.info(" Finished Catch")
        if self.disarm: #TODO should also stop the robot
            self.arm = False #just in case
            self.disarm = False
            self.logger.info("state: IDLE")
            return rp1_fsm.STATE_IDLE
        
        return rp1_fsm.STATE_PITBULL

def main():
    x = RP1_StereoFSM()
    x.start_loop()    
    while False:
        if x.stereo.loop_running: 
            x.stereo.debug_mode = True
            x.stereo.debug_type = "cont"
            time.sleep(5)
            while x.stereo.loop_running:
                cv2.imshow("Colour Image", x.stereo.debug_frame_output)
                # Press q if you want to end the loop
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        x.stereo.loop_running = False
        x.loop_running = False
if __name__ == "__main__":
    print("Delay 1 seconds")
    time.sleep(1)
    main()