import rp1_fsm, time


class RP1_StereoFSM(rp1_fsm.RP1_FSM):
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

if __name__ == "__main__":
    main()