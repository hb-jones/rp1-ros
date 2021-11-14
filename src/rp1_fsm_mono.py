import rp1_fsm, time
from rp1controller import Target


class RP1_MonoFSM(rp1_fsm.RP1_FSM):
    def catching(self):
        #moves to best possible catching position
        if self.disarm: #TODO should also stop the robot
            self.arm = False #just in case
            self.disarm = False
            self.logger.info("state: IDLE")
            return rp1_fsm.STATE_IDLE
        if not self.check_throw_validity():
            self.logger.info("invalid_throw: Returning home")
            home_target = Target()
            self.server.command_set_target(home_target)
            time.sleep(0.5)
            self.arm = False
            self.logger.info("state: IDLE")
            return rp1_fsm.STATE_IDLE
        if self.trajectory_est.get_last_update_age()>self.limit_update_age:
            self.logger.info("state: PITBULL")
            self.pitbull_time = time.time()
            return rp1_fsm.STATE_PITBULL
        return rp1_fsm.STATE_CATCHING

def main():
    x = RP1_MonoFSM()
    x.start_loop()

if __name__ == "__main__":
    main()