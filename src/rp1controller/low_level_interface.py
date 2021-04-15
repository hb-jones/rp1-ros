from logging import config
from rp1controller.trajectory_planners import Target
from .rp1interface import RP1Controller
from typing import Dict
from .typings import Odrive as Odrv, Axis #For type checking etc
import odrive
from odrive.enums import *
import time
from time import sleep
import logging
import threading
import math
    
class LowLevelInterface(): 
    drives_started = False #Flag to indicate if the controller and drives are connected and started
    is_ready = False #Flag to indicate if drives are in closed loop control mode and ready to recieve
    
    thread_updating = False #Flag to indicate thread is running and odometry is being updated
    loop_run_flag = False #Flag for loop to continue running
    loop_complete_flag = False #main_loop() sets this high to indicate it is not hanging
    loop_thread = None #Handle to the loop thread

    axis_state = AXIS_STATE_IDLE

    target_linear = (0,0) 
    target_angular = 0
    target_motor = {"axis_FL": 0, "axis_FR": 0, "axis_BL": 0, "axis_BR": 0}  #Targets for each motor in rps
    target_updated_flag = False #Part of watchdog and checkstate, set high when new command is recieved. If low for too long will stop odrive or watchdog will fire.
    target_changed_flag = False #Determines if input target is changed. Done when a new target is recieved to avoid sending new commands as a result of transform floating point errors
    

    odom_motor_pos_last = {"axis_FL": 0, "axis_FR": 0, "axis_BL": 0, "axis_BR": 0}  #Targets for each motor in rps
    
    odom_updated_time = 0
    odom_linear = (0,0)
    odom_angular = 0

    def __init__(self, main_controller: RP1Controller, external_watchdog = False, debug_func = False):
        self.main_controller = main_controller #Parent controller, needed for access to model, configuration etc
        self.config = self.main_controller.config #Config file containing serial numbers etc
        self.model = self.main_controller.config.model #Kinematic model of the robot
        self.logger = logging.getLogger(__name__) #Creates a logger for use with the base logger
        if debug_func: #Debug mode to only connect to one drive and axis
            self.logger.warning(" - Started LLI in debug mode")
            self.connect_drives = debug_func
            self.connect_drives(self) 
        else:
            self.logger.info(" - Starting LLI")
            self.connect_drives()
        sleep(1) #TODO debug code, reduce or remove
        self.prepare_drives() 
        return
    
    def main_loop(self):
        while self.loop_run_flag:
            if not self.check_state(): #Checks everything is in correct state etc
                self.is_ready = False
                self.logger.warning(" - LLI Loop Error: State check unsucessful. Loop aborting")
                break

            self.update_odometry() 
            
            
            self.loop_complete_flag = True
            sleep(0.05) #TODO reduce if this does not cause issues
        self.logger.info(" - LLI loop shutting down")
        self.thread_updating = False
        self.is_ready = False
        self.drives_started = False #Indicate closed loop control cannot be started until controller successfully enters an idle state
        self.axis_set_state(AXIS_STATE_IDLE)# set axis.state to idle
        if self.check_state():
            self.drives_started = True #Set system ready if shutdown was successful and no errors reported. 

    def update_odometry(self):
        """Updates odometry based on wheel position. Position chosen over velocity as it is likely to be more stable and resistant to varying polling times"""

        motor_pos_current = {}
        for axis_name in self.axes_dict: #get current pos
            axis: Axis = self.axes_dict[axis_name]
            pos = axis.encoder.pos_estimate #Get current position in revolutions
            motor_pos_current.update({axis_name: pos})
        time_current = time.time()
        d_time = time_current-self.odom_updated_time

        current_motor_speed_rad = {} #Current motor angular velocity in radians
        for axis_name in self.axes_dict: #get current angular speed of motor
            rps = (motor_pos_current[axis_name] - self.odom_motor_pos_last[axis_name])/d_time
            rad = self.rps_to_radians(rps)
            current_motor_speed_rad.update({axis_name: rad})
        
        linear_x, linear_y, angular = self.model.transform_velocity_motor_to_base(current_motor_speed_rad)
        if(d_time<1):
            self.odom_linear = (linear_x, linear_y)
            self.odom_angular = angular
        else:
            self.logger.warning(" - Odometry Warning: Time since last update: {}".format(d_time))
        self.odom_updated_time = time_current
        self.odom_motor_pos_last = motor_pos_current      
        #print(f"Odometry updated at {time_current:.2f}. Speed is X:{linear_x:.2f}  Y:{linear_y:.2f}  R:{angular:.2f}") #TODO REMOVE ---------------------
        return

    def set_target(self, linear: tuple, angular: float, log = False): #TODO maybe use custom object or dictionary
        if (self.target_linear == linear) and (self.target_angular == angular): #If new command recieved but not changed exit without updating
            self.target_updated_flag = True
            return
        self.target_linear = linear 
        self.target_angular = angular
        self.target_changed_flag = True
        self.target_updated_flag = True 
        if self.axis_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
            self.set_motor_target(log) #If new target then set motors
        return

    def set_motor_target(self, log = False): 
        
        successful = True

        t_linear = self.target_linear
        t_angular = self.target_angular
        t_motors = self.model.transform_velocity_base_to_motor(t_linear[0], t_linear[1], t_angular)

        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            target_rad = t_motors[axis_name]
            target_rps = self.radians_to_rps(target_rad)
            if log: self.logger.debug("{name}: - Setting target to {tar}".format(name = axis_name, tar = target_rps))
            start_time = time.perf_counter()
            axis.controller.input_vel = target_rps #Sets driver target
            end_time = time.perf_counter()-start_time
            print(f"controller.input_vel time: {end_time}")
            self.target_motor[axis_name] = target_rps
            start_time = time.perf_counter()
            measured_abs_input_vel = abs(axis.controller.input_vel)
            if (measured_abs_input_vel > abs(target_rps) + 0.1 or measured_abs_input_vel < abs(target_rps) - 0.1):
                self.logger.error("{name} - Target Error: Unexpected velocity input. Expected: {t}, currently: {c}".format(name = axis_name, t = target_rps, c = axis.controller.input_vel))
                successful = False
            end_time = time.perf_counter()-start_time
            print(f"input vel check time: {end_time}")
        return successful
   
    def apply_target_to_axis(self, axis: Axis, axis_name, target_rps):
        axis.controller.input_vel = target_rps
        measured_abs_input_vel = abs(axis.controller.input_vel)
        if (measured_abs_input_vel > abs(target_rps) + 0.1 or measured_abs_input_vel < abs(target_rps) - 0.1):
            self.logger.error("{name} - Target Error: Unexpected velocity input. Expected: {t}, currently: {c}".format(name = axis_name, t = target_rps, c = axis.controller.input_vel))
            return False
        return True


    def set_motor_target_direct(self,targ_motor: Dict[str, float]):
        """Test function for direct control of motors. Inputs for each motor in rotations per second"""
        self.logger.debug(" - Setting target in Debug Mode to {}".format(targ_motor))
        if self.target_motor == targ_motor:
            self.target_updated_flag = True
        else:
            self.target_motor = targ_motor
            self.target_updated_flag = True
            self.target_changed_flag = True

        #Apply targets to motor with some checking that it was successful
        successful = True
        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            target_rps = self.target_motor[axis_name]
            self.logger.debug("{name}: - Attempting to set target to {tar}".format(name = axis_name, tar = target_rps))
            axis.controller.input_vel = target_rps
            if (abs(axis.controller.input_vel) > abs(target_rps)+0.1 or abs(axis.controller.input_vel) < abs(target_rps) - 0.1):
                self.logger.error("{name} - Target Error: Unexpected velocity input. Expected: {t}, currently: {c}".format(name = axis_name, t = target_rps, c = axis.controller.input_vel))
                successful = False
        return successful

    def soft_stop(self): #TODO
        #Sets target speed of all wheels to be 0, only returns true when this is complete
        #Should call hard stop if this takes too long
        return True
    def hard_stop(self): #TODO 
        #Should cut power to motors
        return

    def start_loop(self): 
        """Starts the main loop in it's own thread""" 
        self.check_state(True)
        if not self.drives_started:
            self.logger.warning(" - LLC Loop could not be started as system is not ready")
            return False
        self.loop_run_flag = True
        if self.axis_state ==AXIS_STATE_CLOSED_LOOP_CONTROL:
            self.is_ready = True
        else:
            self.logger.warning(" - Loop Warning: Starting loop in axis_state: {}".format(self.axis_state))
        self.logger.info(" - Starting LLC Loop")
        
        self.loop_thread = threading.Thread(target=self.main_loop)
        self.thread_updating = True
        self.loop_thread.start()
        return  True
    
    def stop_loop(self):
        """Stops the main thread if it exists"""
        self.logger.debug(" - Attempting  to stop LLC loop...")
        if self.loop_thread is not None:
            self.soft_stop()
            self.loop_run_flag = False
            self.loop_thread.join()
            self.logger.debug(" - LLC loop stopped successfully")
            if self.drives_started:
                self.logger.info(" - LLC in idle state")
        else:
            self.logger.debug(" - no LLC loop to stop")
        return True


    def connect_drives(self):
        """Starts front and rear Odrives"""
        def get_drive(serial: str = "")->Odrv: #TODO add individual time limit so problematic drive can be more readily identified
            self.logger.debug(" - Attempting connection with Odrive {}".format(serial))
            drive = odrive.find_any(serial_number=serial)
            self.logger.debug(" - Odrive {} connected successfully".format(serial))
            return drive
        def get_axis(drive: Odrv, index: int = 0):
            if index == 0:
                return drive.axis0
            elif index == 1:
                return drive.axis1
            else: 
                self.logger.error(" - Drive Error: {} is not a valid axis index".format(index))
                return None
        self.logger.debug(" - Attempting to connect to Odrives")
        #TODO this needs a time limit for whole start up sequence
        self.odrvF = get_drive(self.config.odrvF_serial_number) #Connect both Odrives
        self.odrvB = get_drive(self.config.odrvB_serial_number)
        
        self.axes_dict = {} #Convenience dictionary for iterating throgh each axis
        self.axis_FL = get_axis(self.odrvF, 1) ; self.axes_dict.update({"axis_FL" : self.axis_FL}) #Get each axis, assign handle and add to dict
        self.axis_FR = get_axis(self.odrvF, 0) ; self.axes_dict.update({"axis_FR" : self.axis_FR}) 
        self.axis_BL = get_axis(self.odrvB, 0) ; self.axes_dict.update({"axis_BL" : self.axis_BL})
        self.axis_BR = get_axis(self.odrvB, 1) ; self.axes_dict.update({"axis_BR" : self.axis_BR})

        self.logger.info(" - Drives Connected")
        
    def prepare_drives(self):
        self.logger.debug(" - Preparing drives")
        if not self.check_errors(True): #Check errors
            self.drives_started = False
            return False
        
        if not self.update_configuration(): #Adjsts odrive config based on rp1 config file, max speed etc
            self.drives_started = False
            return False
        
        self.axis_set_control_mode(CONTROL_MODE_VELOCITY_CONTROL) #Puts control mode into direct drive mode
        self.axis_set_input_mode(INPUT_MODE_VEL_RAMP) #Turn on direct velocity control
        
            
        self.axis_set_state(AXIS_STATE_CLOSED_LOOP_CONTROL) #change axes states 
        

        if not self.check_state(): #Check errors
            self.drives_started = False
            return False
        #TODO check is ready (encoder ready, motor ready etc) This will need to be disabled for testing
        self.drives_started = True
        self.logger.info(" - Drives started and ready")
        return True

    def axis_set_state(self, state = AXIS_STATE_IDLE):
        """Changes each axis state. Returns true if successful"""
        self.logger.debug(' - Performing full axis state change to {}'.format(state))
        self.axis_state = state
        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            if axis.current_state != AXIS_STATE_IDLE and state != AXIS_STATE_IDLE: #TODO this is debug code
                self.logger.warning("{name}: - State Error: Current state is {current} and not IDLE. Attempting to fix...".format(name = axis_name, current = axis.current_state))
                axis.requested_state = AXIS_STATE_IDLE
                sleep(0.1)
                self.logger.info("{name}: - State Error: Current state is {current}".format(name = axis_name, current = axis.current_state))
            self.logger.debug("{name}: - Setting state to {state}".format(state=state, name=axis_name))
            axis.requested_state = state

        sleep(0.02) 

        error = False
        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            if axis.current_state != state:
                self.logger.error("{name}: - State Error: Current state is {current} when {req} was requested.".format(name = axis_name, current = axis.current_state, req = state))
                error = True
            else: 
                self.logger.debug("{name}: - State change to {req} was successfull".format(name = axis_name, req = state))
        if error: return False
        else: return True

    def axis_set_control_mode(self, mode = CONTROL_MODE_VELOCITY_CONTROL):
        """Sets the control mode of each axis, should be velocity usually"""
        #Sets the control mode to be direct velocity control for each axis
        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            axis.controller.config.control_mode = mode
            sleep(0.1) #TODO Remove or reduce
            if axis.controller.config.control_mode != mode:
                self.logger.error("{name}: - Controller Error: Current mode is {current} when {req} was requested.".format(name = axis_name, current = axis.controller.config.control_mode, req = mode))
        return
    
    def axis_set_input_mode(self, mode = INPUT_MODE_PASSTHROUGH, ramp_rate = 0):
        """Sets input mode for each axis to be passthrhough unless otherwise specified"""
        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            if mode == INPUT_MODE_VEL_RAMP and ramp_rate != 0:
                axis.controller.config.vel_ramp_rate = ramp_rate
            
            axis.controller.config.input_mode = mode
        return
    
    def rps_to_radians(self,rps): 
        return rps*(2*math.pi)
    def radians_to_rps(self,rad):
        return rad/(2*math.pi)

    def update_configuration(self): #TODO
        #Updates the configuration of the axes based on latest config file (or config object)
        # TODO check whether handle to master config file updates correctly when modified
        # Potentially only update in idle mode? or only for some parameters? Maybe full config update if needed
        #ramping constants etc

        for axis_name in self.axes_dict:
            axis: Axis = self.axes_dict[axis_name]
            axis.controller.config.pos_gain = self.main_controller.config.pos_gain
            axis.controller.config.vel_gain = self.main_controller.config.vel_gain
            axis.controller.config.vel_integrator_gain = self.main_controller.config.vel_integrator_gain
            axis.controller.config.vel_ramp_rate = self.main_controller.config.vel_ramp_rate


        return True

    def check_errors(self, startup = False, log = False):
        """Checks for errors in any axis, returns true if no error is found. If startup is true  this will reset any SPI errors""" 
        if startup:
            self.check_spi_errors()
        error_present = False
        for axis_name in self.axes_dict: #Iterate through axes
            
            axis = self.axes_dict[axis_name]
            axis_error = axis.error #Copy error values only once to reduce polling time TODO that didnt work for some reason
            motor_error = axis.motor.error
            encoder_error = axis.encoder.error
            controller_error = axis.controller.error


            if (axis_error+motor_error+encoder_error+controller_error>0):
                error_present = True
                self.logger.warning("{}: - Error detected on axis".format(axis_name))

                if (axis_error>0):
                    self.logger.error("{name}: - Axis Error: {error}".format(name = axis_name, error = axis_error))

                if (motor_error>0):
                    self.logger.error("{name}: - Motor Error: {error}".format(name = axis_name, error = motor_error))

                if (encoder_error>0):
                    self.logger.error("{name}: - Encoder Error: {error}".format(name = axis_name, error = encoder_error))

                if (controller_error>0):
                    self.logger.error("{name}: - Controller Error:{error}".format(name = axis_name, error = controller_error))

        if error_present: return False
        else:
            if log: self.logger.debug(' - Errors checked, none found')
            return True
        
    def check_spi_errors(self):
        """Check for errors in all axes, will attempt to reset any SPI errors once. Returns true if no error is found"""
        sleep(0.1)
        for axis_name in self.axes_dict: #Iterate through axes
            axis = self.axes_dict[axis_name]
            encoder_error = axis.encoder.error
            if((encoder_error == ENCODER_ERROR_ABS_SPI_COM_FAIL or encoder_error == ENCODER_ERROR_ABS_SPI_NOT_READY)): 
                self.logger.warning("{name}: - SPI Error: {error}. Attempting to reset...".format(name = axis_name, error = axis.encoder.error))
                axis.clear_errors() #Clears existing errors 
                sleep(0.1) #wait again to see if error reappears
                encoder_error = axis.encoder.error
                if((encoder_error == ENCODER_ERROR_ABS_SPI_COM_FAIL or encoder_error == ENCODER_ERROR_ABS_SPI_NOT_READY)): #Looks for errors again
                    self.logger.info("{name}: - SPI Error was reset successfully".format(name = axis_name))
                else:
                    self.logger.error("{name}: - SPI Error: {error}. Reset unsuccessful".format(name = axis_name, error = axis.encoder.error))
        return 

    def check_state(self, full_check = False, log = False): #TODO
        return_val = True
        if full_check:
            if log: self.logger.debug(" - Full state check started...") #TODO
            # check things like voltages current etc
            #Log

            #check if system is in correct state
            #check time since last command, set velocity taget to 0 if too long
            # stop loop if error or problem found
        
            
        if not self.check_errors():
            self.drives_started = False
            return_val =  False
        if ((not self.drives_started) and (self.is_ready or self.loop_run_flag)):
            return_val =  False
        if return_val:
            if log: self.logger.debug(" - State check sucessfull")
        else:
            self.logger.error(" - State check failed")
        return return_val #TODO More comprehensive check errors, also check voltages etc and potentially logs them
        


def debug_connect_drives(self):
    """debug version of start drives with only one axis"""
    def get_drive(serial: str = "")->Odrv: #TODO add individual time limit so problematic drive can be more readily identified
        self.logger.debug(" - Attempting connection with Odrive {}".format(serial))
        drive = odrive.find_any(serial_number=serial)
        self.logger.debug(" - Odrive {} connected successfully".format(serial))
        return drive
    def get_axis(drive: Odrv, index: int = 0)->Axis:
        if index == 0:
            return drive.axis0
        elif index == 1:
            return drive.axis1
        else: #TODO throw proper error
            return False
    self.logger.debug(" - Attempting to connect to Odrives")
    #TODO this needs a time limit for whole start up sequence
    self.odrvF = get_drive(self.config.odrvF_serial_number) #Connect both Odrives
    
    self.axes_dict = {} #Convenience dictionary for iterating throgh each axis
    self.axis_FL = get_axis(self.odrvF, 0) ; self.axes_dict.update({"axis_FL" : self.axis_FL}) #Get each axis, assign handle and add to dict
    self.logger.info(" - Drive Connected")

    return True

def get_target(target):
    tar = {"axis_FL": target}

    return tar

def get_single_target(axis_name: str, val: float):
    tar = {"axis_FL": 0, "axis_FR": 0, "axis_BL": 0, "axis_BR": 0}
    tar[axis_name] = val    
    return tar


def debug_update_target(x,y,w,llc):
    llc.set_target((x,y),w)
    print("Target: x:{x}, y:{y}, w:{w}".format(x=x,y=y,w=w))

def print_odom(llc):
    x, y = llc.odom_linear
    w = llc.odom_angular
    print("Base_X: {x}, Base_Y: {y}, Base_w: {w}\n".format(x =x,y=y,w=w))




if __name__ == "__main__":
    import keyboard

    HLC = RP1Controller()
    cnt = LowLevelInterface(HLC)
    speed_linear = 2
    speed_radial = 0.8
    cnt.start_loop()
    loop = True
    def fwd():
        cnt.set_target((speed_linear,0),0)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def bck():
        cnt.set_target((-speed_linear,0),0)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def lft():
        cnt.set_target((0,-speed_linear),0)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def rgt():
        cnt.set_target((0,speed_linear),0)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def rot_left():
        cnt.set_target((0,0),-speed_radial)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def rot_rgt():
        cnt.set_target((0,0),speed_radial)
        sleep(0.1)
        cnt.set_target((0,0),0)
    def stp():
        cnt.set_target((0,0),0)
    def shut_down():
        cnt.stop_loop()
        loop = False
        

    keyboard.add_hotkey('w', fwd)
    keyboard.add_hotkey('s', bck)
    keyboard.add_hotkey('a', lft)
    keyboard.add_hotkey('d', rgt)
    keyboard.add_hotkey('q', rot_left)
    keyboard.add_hotkey('e', rot_rgt)
    keyboard.add_hotkey(' ', stp)
    keyboard.add_hotkey('r', stp)
    keyboard.add_hotkey('t', shut_down)

    while(loop):
        sleep(1)
        pass


    #cnt.stop_loop()



    
        

