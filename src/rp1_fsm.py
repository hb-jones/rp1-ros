import time, abc, threading, logging, logging.config
from rp1controller.communications import RP1Server
from rp1controller.trajectory_planners import LocalVelocityControl, Target, WorldVelocityControl, WorldPoseControl
from rp1_gamepad import GamepadInput
from rp1controller.rp1config import RP1Configuration
from vision import stereo, trajectory_estimation

STATE_INVALID = -1
STATE_PRESTARTUP = 0
STATE_STARTUP = 1
STATE_IDLE = 2
STATE_ARMED = 3
STATE_CATCHING = 4
STATE_BADTHROW = 5
STATE_PITBULL = 6
STATE_FINISHED = 7

logging.config.fileConfig('logging.conf',disable_existing_loggers=False)

#TODO
#Make sure all armed states have a path to disarming
#Make sure robot cannot be moving after disarm
#Write logging/debug outputs, and publish to file depending on timestamp.
#Write monocular shit
#That includes terminal phase

class RP1_FSM(abc.ABC):
    catch_limit_dist = 1.3  #max metres to intercept for valid throw
    catch_limit_time = 0.5  #seconds until intercept for valid throw
    limit_update_age = 0.1  #Time from last stereo datapoint to switch to terminal, will need to be tuned
    limit_pitbull_age = 3   #Time to remain in terminal state
    targeting_delay = 0.1   #TODO This is kinda slow

    def __init__(self):
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        self.logger.info(f"initialise: General Initialisation")
        self.state = STATE_PRESTARTUP
        self.arm = False
        self.disarm = False

        self.last_target = Target()
        self.server = RP1Server("192.168.137.1")
        time.sleep(3)
        self.gamepad = GamepadInput(self.server)
        self.gamepad.variable_func = self.gamepad_arm_rp1
        
        self.loop_running = False
        self.logger.info(f"initialise: General Initialisation Finished")
        

    def start_loop(self):
        self.loop_thread = threading.Thread(target=self.main_loop)
        self.loop_running = True
        self.loop_thread.start()
        self.logger.info("initialise: Main loop started")

    def main_loop(self): #TODO should always check for a disarm!!!!
        while self.loop_running:
            state = self.state
            if state == STATE_PRESTARTUP:
                self.state = self.prestartup()
            elif state == STATE_STARTUP:
                self.state = self.startup()
            elif state == STATE_IDLE:
                self.state = self.idle()
            elif state == STATE_ARMED:
                self.state = self.armed()
            elif state == STATE_BADTHROW:
                self.state = self.badthrow()
            elif state == STATE_CATCHING:
                self.state = self.catching()
            elif state == STATE_PITBULL:
                self.state = self.pitbull()
            
            else:
                self.state = self.invalid()
            
    def invalid(self): #TODO
        #Should report that the state is invalid and prevent the startup of any new states.
        #Should try and safe the robot but catch error if this fails.
        self.logger.warn("invalid_state: State is currently invalid")
        return STATE_INVALID


    def prestartup(self):
        #Waiting, start cameras
        #Start Traj est
        self.trajectory_est = trajectory_estimation.TrajectoryEstimator()
        #start Stereo
        self.stereo = stereo.Stereo(self.trajectory_est.stereo_publisher)
        self.logger.info("initialise: Prestartup and cameras active")
        time.sleep(1)
        return STATE_STARTUP
    
    def startup(self):
        #Sets limits in case config has changed locally without updating remote
        speed_max = RP1Configuration.linear_velocity_max
        speed_updated = self.server.command_set_speed_limit(speed_max, expect_response=True, log=True)
        while not speed_updated:
            time.sleep(0.2)
            speed_updated = self.server.command_set_speed_limit(speed_max, expect_response=True, log=True)
        
        acceleration = RP1Configuration.acceleration_max
        acceleration_updated = self.server.command_set_acceleration_limit(acceleration, expect_response=True, log=True)
        while not acceleration_updated:
            time.sleep(0.2)
            acceleration_updated = self.server.command_set_acceleration_limit(acceleration, expect_response=True, log=True)
            
        planner_updated = self.server.command_set_planner(WorldPoseControl, expect_response=True, log=True)
        while not planner_updated:
            continue #TODO
            time.sleep(2)
            planner_updated = self.server.command_set_planner(WorldPoseControl, expect_response=True, log=True)
        
        self.trajectory_est.clear_points()#Clears the current trajectory
        
        self.logger.info("initialise: Robot started and idle")

        return STATE_IDLE

    def idle(self):
        #Waiting for arming signal, then resets localisation and prepares to catch ball
        self.disarm = False
        self.stereo.loop_running = False
        if not self.arm:
            return STATE_IDLE
        else:
            self.arm = False
            odom_reset = self.server.command_reset_localisation(expect_response=True, log=True)
            while not odom_reset:
                time.sleep(0.5)
                odom_reset = self.server.command_reset_localisation(expect_response=True, log=True)
            time.sleep(0.5)
            self.trajectory_est.clear_points()#Clears the current trajectory
            self.logger.info("state: ARMED")
            self.stereo.start_loop()
            return STATE_ARMED
            #TODO potentially should also switch mode into correct one?????
    
    def armed(self):
        #Waiting for recieved throw traj, moves to either catching mode or invalid throw
        if self.disarm:
            self.arm = False #just in case
            self.disarm = False
            self.logger.info("state: IDLE")
            return STATE_IDLE
        elif not self.check_for_throw():
            time.sleep(0.05)
            return STATE_ARMED
        elif not self.check_throw_validity():
            self.logger.info("state: BADTHROW")
            return STATE_BADTHROW
        else:
            self.logger.info("state: CATCHING")
            self.logger.info(f" Intercept {self.trajectory_est.get_impact_point()}")
            return STATE_CATCHING
        
    def badthrow(self):#TODO!!!!!!!!!!!!!!!!!!
        #Reset everything and disarm
        self.logger.info("state: IDLE")
        return STATE_IDLE
    
    def catching(self):
        #moves to best possible catching position
        if self.disarm: #TODO should also stop the robot
            self.arm = False #just in case
            self.disarm = False
            self.logger.info("state: IDLE")
            return STATE_IDLE
        if not self.check_throw_validity():
            self.logger.info("invalid_throw: Returning home")
            home_target = Target()
            self.server.command_set_target(home_target)
            time.sleep(0.5)
            self.arm = False
            self.logger.info("state: IDLE")
            return STATE_IDLE
        if self.trajectory_est.get_last_update_age()>self.limit_update_age:
            self.logger.info("state: PITBULL")
            self.pitbull_time = time.time()
            return STATE_PITBULL
        intercept = self.trajectory_est.get_impact_point()
        target= Target()
        target.world_point = (intercept.x,intercept.y)
        if target.world_point == self.last_target.world_point:
            return STATE_CATCHING
        else:
            self.last_target = target
            self.logger.info(f"moving_to_target {target.world_point}")
            self.server.command_set_target(target)
            time.sleep(self.targeting_delay)
            return STATE_CATCHING

    def check_for_throw(self):
        """Checks if a throw has been detected by the vision system/s"""
        if self.trajectory_est.get_impact_point() == False:
            return False
        return True
         
    def check_throw_validity(self):
        """Checks the vailidity of a throw and if catching is possible"""
        impact = self.trajectory_est.get_impact_point()
        if impact == False:
            self.logger.info("invalid_throw: No impact point")
            return False
        if abs(impact.x)>self.catch_limit_dist or abs(impact.y)>self.catch_limit_dist:
            self.logger.info(f"invalid_throw: Intercept too far away: {impact}")
            return False
        time_to_impact = impact.timestamp-time.time()
        if time_to_impact<self.catch_limit_time and self.state != STATE_CATCHING:
            self.logger.info(f"invalid_throw: Intercept too soon: {time_to_impact}s")
            return False
        return True

    def pitbull(self): #TODO
        if time.time()-self.pitbull_time>self.limit_pitbull_age:
            self.disarm = True
            self.logger.info(" Finished Catch")
        if self.disarm: #TODO should also stop the robot
            self.arm = False #just in case
            self.disarm = False
            self.logger.info("state: IDLE")
            return STATE_IDLE
        self.server.command_custom()
        time.sleep(self.targeting_delay)
        return STATE_PITBULL

    def trigger_disarm(self):
        self.state == STATE_IDLE
        self.arm = False
        self.disarm = True

    def gamepad_arm_rp1(self):
        #Should arm the system
        if self.state != STATE_IDLE:
            self.arm = False
            self.disarm = True
        elif self.state == STATE_IDLE:
            self.arm = True
            self.disarm = False
    


def main():
    fsm = RP1_FSM()
    fsm.start_loop()

if __name__ == "__main__":
    main()