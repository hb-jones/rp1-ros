from rp1controller import Target
from rp1controller.trajectory_planners import LocalVelocityControl, WorldVelocityControl, WorldPoseControl
from rp1controller import RP1Server
from time import sleep
from inputs import get_gamepad
import threading

IP_laptop = "192.168.137.1"

class GamepadInput():
    axis_FB = "ABS_Y"
    axis_LR = "ABS_X"
    axis_rot = "ABS_RX"
    axis_deadzone = 0.2

    button_UP = "BTN_TR"
    button_DN = "BTN_TL"
    button_VAR = "BTN_EAST" #TODO replace with custom function
    button_BRK = "BTN_SOUTH"
    button_MODE = "BTN_WEST"
    button_ADVANCE = "BTN_NORTH"

    button_PRP = "ABS_HAT0Y"
    state_PRP_UP = -1
    state_PRP_DN = 1

    button_INT = "ABS_HAT0X"
    state_INT_UP = 1
    state_INT_DN = -1

    speed_limit_rot = 1
    speed_limit_linear = 1
    speed_limit_step = 0.2

    gamepad_loop_flag = False
    gamepad_loop_handle = None
    control_loop_flag = False
    control_loop_handle = None

    target = Target()
    target_updated = False
    control_modes = [LocalVelocityControl, WorldVelocityControl, WorldPoseControl]
    control_mode_index = 0

    variable_func = lambda a: print("No variable function set")
    emergency_brake_func = lambda a: print("No additional brake function set")


    def __init__(self, server: RP1Server, log=False):

        self.server: RP1Server = server
        self.log = log

        self.gamepad_loop_handle = threading.Thread(target=self.listen_to_gamepad, daemon=False) #TODO might need to be a daemon
        self.gamepad_loop_flag = True
        self.gamepad_loop_handle.start()

        self.control_loop_handle = threading.Thread(target=self.control_loop, daemon=True)
        self.control_loop_flag = True
        self.control_loop_handle.start()

        pass
    
    def __del__(self):
        print("Stopping gamepad control")
        self.control_loop_flag = False
        self.gamepad_loop_flag = False
        if self.control_loop_handle is not None:
            self.control_loop_handle.join()
        if self.gamepad_loop_handle is not None:
            self.gamepad_loop_handle.join()


    def listen_to_gamepad(self):
        while self.gamepad_loop_flag:
            try:
                events = get_gamepad()
            except:
                print("Gamepad Disconnected")
                self.gamepad_loop_flag = False
                self.brake()
            for event in events:
                if event.code == self.button_BRK: #Emergency stop
                    self.gamepad_loop_flag = False
                    self.brake()
                    self.emergency_brake_func()
                    print("EMERGENCY BRAKE")
                    return
                if event.code == self.axis_FB:
                    self.update_target("axis_FB",event.state)
                if event.code == self.axis_LR:
                    self.update_target("axis_LR",event.state)
                if event.code == self.axis_rot:
                    self.update_target("axis_rot",event.state)
                if event.code == self.button_UP and event.state == 1:
                    self.speed_limit_linear += self.speed_limit_step
                if event.code == self.button_DN and event.state == 1:
                    self.speed_limit_linear += self.speed_limit_step
                if event.code == self.button_VAR and event.state == 1: #TODO
                    self.variable_func()
                if event.code == self.button_MODE and event.state == 1:
                    self.change_mode()
                if event.code == self.button_ADVANCE and event.state == 1:
                    self.get_location()
                if event.code == self.button_PRP:
                    if event.state == self.state_PRP_UP:
                        pass#self.update_PID("proportional", True) 
                    elif event.state == self.state_PRP_DN:
                        pass #self.update_PID("proportional", False) 
                if event.code == self.button_INT:
                    if event.state == self.state_INT_UP:
                        pass #self.update_PID("integrator", True) 
                    elif event.state == self.state_INT_DN:
                        pass #self.update_PID("integrator", False) 

    def control_loop(self): #Sends the updated target 10 times per second so network is not overloaded
        while self.control_loop_flag:
            sleep(0.1)
            self.send_target()


    def curve(self, input):
        input = input/32000
        if input<0:
            sign = -1
        else:
            sign = 1
        input_unsigned = abs(input)
        if input_unsigned<self.axis_deadzone:
            output_unsigned = 0
        else:
            output_unsigned = input_unsigned*1/(1-self.axis_deadzone)-self.axis_deadzone
        if output_unsigned >1: output_unsigned = 1
        output = output_unsigned*sign
        return output

    def update_target(self, t_axis, value, urgent=False):
        speed = self.curve(value)
        self.target_updated = True
        if t_axis == "axis_FB":
            lin_speed = speed*self.speed_limit_linear
            LR_speed = self.target.local_velocity[1]
            self.target.local_velocity = (lin_speed, LR_speed)
            self.target.world_velocity = (lin_speed, LR_speed)
        elif t_axis == "axis_LR":
            lin_speed = -speed*self.speed_limit_linear
            FB_speed = self.target.local_velocity[0]
            self.target.local_velocity = (FB_speed, lin_speed)
            self.target.world_velocity = (FB_speed, lin_speed)
        elif t_axis == "axis_rot":
            a_speed = -speed*self.speed_limit_rot
            self.target.angular_velocity = a_speed

        if urgent:
            self.send_target()
        
    def send_target(self):
        if self.target_updated:
            self.server.command_set_target(self.target, log=self.log)
            self.target_updated = False
        return

    def brake(self):
        self.server.command_set_target(Target(), log=self.log)
        return
    
    def change_mode(self):
        self.server.command_set_planner(self.control_modes[self.control_mode_index], log=self.log)
        self.control_mode_index+=1
        if self.control_mode_index == len(self.control_modes):
            self.control_mode_index = 0
        #go through array of TMSs, support for pose is not needed. Use for pausing test
        return
    
    def get_location(self):
        location = self.server.command_get_location(expect_response=True, log = self.log)
        print(location) #TODO maybe improve print format
        return






if __name__ == "__main__":
    server = RP1Server(IP_laptop)
    sleep(3)
    print("Starting Gamepad")
    #server.command_get_location()
    gamepad_controller = GamepadInput(server)
