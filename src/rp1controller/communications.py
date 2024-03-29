from .odometry_system import VelocityPose
import socket, pickle, time, threading
from rp1controller import Target, RP1Controller
from .trajectory_planners import ControlMode

class Command:
    def __init__(self, command_name, function = None, args = None, expect_response = False, log = False):
        self.command_name  = command_name
        self.function = function
        self.args = args
        self.expect_response = expect_response
        self.log = log


class RP1Communications:
    ip_server = None
    rp1socket = None

    def __init__(self, ip):
        self.ip_server = ip
        self.setup_socket()
        return

    def __del__(self):
        self.rp1socket.close()

    def setup_socket(self):
        self.rp1socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return
    
    def send_data(self, data_to_send): #TODO add handling for failed send
        data = pickle.dumps(data_to_send)
        try:
            self.rp1socket.send(data)
            return True
        except:
            print("Data was not sent")
            return False

    def get_response(self):
        self.rp1socket.settimeout(1.0)
        try:
            msg = self.rp1socket.recv(2048)
            data = pickle.loads(msg)
            return data
        except:
            print("No response recieved")
            return False

    def command_watchdog(self):
        return

    def command_set_target(self, target, expect_response = False, log = False):
        if log:
            print(f"Setting target to {target}")
        
        if type(target) != Target:
            print(f"Expected {Target}, recieved: {type(target)}")
            return False
        return True

    def command_set_planner(self, planner, expect_response = False, log = False):
        if log:
            print(f"Setting planner to {planner}")
        if not issubclass(planner,ControlMode):
            print(f"Expected {ControlMode} derivitive, recieved {planner}")
            return False
        return True

    def command_set_speed_limit(self, speed_limit, expect_response = True, log = False):
        if log:
            print(f"Setting speed limit to {speed_limit}m/s")
        if not (type(speed_limit) == int or type(speed_limit) == float):
            print(f"Expected {float} or {int}, recieved {type(speed_limit)}")
            return False
        return True

    def command_set_acceleration_limit(self, acceleration_limit, expect_response = True, log = False):
        if log:
            print(f"Setting acceleration limit to {acceleration_limit}m/s^2")
        if not (type(acceleration_limit) == int or type(acceleration_limit) == float):
            print(f"Expected {float} or {int}, recieved {type(acceleration_limit)}")
            return False
        return True
        
    def command_reset_localisation(self, expect_response = False, log = False):
        if log:
            print("Resetting Localisation")
        return True

    def command_get_location(self, log = False):
        if log:
            print("Getting Location")
        return True

    def command_custom(self, log = False):
        if log:
            print("Custom function")
        return True

class RP1Server(RP1Communications):
    watchdog_delay = 0.3 #How long between watchdog feeds
    watchdog_loop_flag = False
    watchdog_loop_handle = None
    watchdog_fail_count = 0
    watchdog_fail_max = 10
    
    last_command_time = 0

    def __init__(self, ip):
        super().__init__(ip=ip)

        self.watchdog_loop_flag = True
        self.watchdog_loop_handle = threading.Thread(target=self.watchdog_loop, daemon=True)
        self.watchdog_loop_handle.start()

    def __del__(self):
        print("Stopping Server")
        self.watchdog_loop_flag = False
        self.watchdog_loop_handle.join()
        self.clientsocket.close()
        return super().__del__()

    def setup_socket(self):
        super().setup_socket()
        self.rp1socket.bind((self.ip_server, 1066))
        self.rp1socket.listen(5)
        self.clientsocket, address = self.rp1socket.accept()
        self.clientsocket.setblocking(False)
        print(f"Connection from {address} has been established.")
        return

    def send_data(self, data_to_send):
        data = pickle.dumps(data_to_send)
        try:
            self.clientsocket.send(data)
            self.last_command_time = time.time()
            return True
        except Exception as e:
            print(f"Data was not sent: {e}")
            return False

    def get_response(self):
        self.clientsocket.settimeout(1.0)
        try:
            msg = self.clientsocket.recv(2048)
            data = pickle.loads(msg)
            return data
        except:
            print("No response recieved")
            return False

    def watchdog_loop(self):
        while self.watchdog_loop_flag:
            time_since_last_command = time.time()-self.last_command_time
            if time_since_last_command>self.watchdog_delay:
                self.command_watchdog()
            time.sleep(self.watchdog_delay/4)

    def command_watchdog(self):
        super().command_watchdog()
        watchdog = Command("watchdog")
        if not self.send_data(watchdog):
            self.watchdog_fail_count += 1
        if self.watchdog_fail_count>self.watchdog_fail_max:
            print("Too many failed watchdog requests")
            self.watchdog_loop_flag = False

    def command_set_target(self, target, expect_response = False, log = False):
        success = super().command_set_target(target, expect_response=expect_response, log=log)
            
        if not success:
            return False

        set_target = Command("set_target", function=RP1Client.command_set_target, args=target, expect_response=expect_response, log=log)
        self.send_data(set_target)

        if expect_response:
            response = self.get_response()
            if not response:
                print("Target not set successfully")
                return False
            else:
                return True

    def command_set_planner(self, planner, expect_response = False, log = False): #TODO needs to be tested to make sure it can differnetiate between control modes
        """Planner should be the type of planner to use"""
        success = super().command_set_planner(planner, expect_response, log)
        
        if not success:
            return False

        set_planner = Command("set_planner", function=RP1Client.command_set_planner, args=planner, expect_response=expect_response, log=log)
        self.send_data(set_planner)

        if expect_response:
            response = self.get_response()
            if response == False:
                return False
            if not issubclass(response,ControlMode):
                print("Response of incorrect type")
                return False
            if planner != response:
                print(f"Planner not set correctly. Expected {planner}, instead recieved {response}")
                return False
            return True

    def command_set_speed_limit(self, speed_limit, expect_response = True, log = False):
        success = super().command_set_speed_limit(speed_limit, expect_response, log)

        if not success:
            return False

        set_speed_limit = Command("set_speed_limit", function=RP1Client.command_set_speed_limit, args=speed_limit, expect_response=expect_response, log=log)
        self.send_data(set_speed_limit)

        if expect_response:
            response = self.get_response()
            if not (type(response) == int or type(response) == float):
                print(f"Expected {float} or {int} response, recieved {type(response)}")
                return False
            if response != speed_limit:
                print(f"Speed limit was not successfully updated. Expected {speed_limit}, instead recieved {response}")
                return False
            return True

    def command_set_acceleration_limit(self, acceleration_limit, expect_response = True, log = False):
        success = super().command_set_acceleration_limit(acceleration_limit, expect_response=expect_response, log=log)

        if not success:
            return False

        set_acceleration_limit = Command("set_acceleration_limit", function=RP1Client.command_set_acceleration_limit, args=acceleration_limit, expect_response=expect_response, log=log)
        self.send_data(set_acceleration_limit)

        if expect_response:
            response = self.get_response()
            if not (type(response) == int or type(response) == float):
                print(f"Expected {float} or {int} response, recieved {type(response)}")
                return False
            if response != acceleration_limit:
                print(f"Speed limit was not successfully updated. Expected {acceleration_limit}, instead recieved {response}")
                return False
            return True

    def command_reset_localisation(self, expect_response = False, log = False):
        success = super().command_reset_localisation(expect_response=expect_response, log=log)

        reset_localisation = Command("reset_localisation",function=RP1Client.command_reset_localisation, expect_response=expect_response, log=log)
        self.send_data(reset_localisation)

        if expect_response:
            response = self.get_response()
            if response:
                if log:
                    print("Odometry successfully reset")
                return True
            else:
                print("Odometry was not reset")
                return False

    def command_get_location(self, expect_response = True, log = False):
        super().command_get_location(log=log)

        get_location = Command("get_location", function=RP1Client.command_get_location, expect_response=expect_response, log=log)
        self.send_data(get_location)

        if expect_response:
            response = self.get_response()
            if response == False:
                return False
            if type(response) != VelocityPose:
                print("Response of incorrect type")
                return False
            
            if log:
                print(response) 
            return response

    def command_custom(self, log = False):
        success = super().command_custom(log=log)
        if not success:
            return False
        custom_command = Command("custom", function=RP1Client.command_custom, expect_response=False, log=log)
        print(f"Custom Command Sent: {time.time()}")
        self.send_data(custom_command)
        return True

class RP1Client(RP1Communications):
    timeout = 2.0
    loop_flag = False 
    loop_handle = None
    HLC: RP1Controller = None

    def __init__(self, ip, custom_function = None):
        super().__init__(ip=ip)
        self.custom_function = custom_function
        self.HLC = RP1Controller()

        self.loop_flag = True
        self.loop_handle = threading.Thread(target=self.comms_loop)
        self.loop_handle.start()
        return
    
    def __del__(self):
        print("Stoping Client")
        if self.HLC is not None:
            self.HLC.set_target(Target())
        self.loop_flag = False
        self.loop_handle.join()
        super().__del__()

    def setup_socket(self):
        super().setup_socket()
        self.rp1socket.connect((self.ip_server, 1066))
        print(f"Connection to server has been established.")
        return

    def comms_loop(self):
        self.rp1socket.settimeout(self.timeout)
        unpickle_fail_count = 0
        unpickle_fail_max = 5
        while self.loop_flag:
            try:
                msg = self.rp1socket.recv(2048)
                try:
                    data = pickle.loads(msg)
                except:
                    unpickle_fail_count += 1 
                    print(f"Failed to unpickle: {unpickle_fail_count}")
                    if unpickle_fail_count>unpickle_fail_max:
                        self.handle_timeout()
                        return
                self.handle_data(data)
            except Exception as e:
                print(f"Recv failed: {e}")
                self.handle_timeout()
                return
        return
    
    def handle_data(self, data: Command):
        if type(data) != Command:
            print("Command of incorrect type")
            return
        if data.command_name == "":
            print("No command name")
            return
        if data.log:
            print(f"Recieved Command {data.command_name}")
        if data.function is not None:
            if data.args is not None: 
                data.function(self, data.args,  expect_response = data.expect_response, log = data.log)
            else:
                data.function(self, expect_response = data.expect_response, log = data.log)
        return

    def handle_timeout(self):
        self.loop_flag = False
        self.HLC.set_target(Target())
        #TODO Should kill odrives and stop vehicle
        print("Watchdog expired on client")
        return
    
    def command_watchdog(self):
        super().command_watchdog()
        return

    def command_set_target(self, target, expect_response = False, log = False):
        success = super().command_set_target(target, expect_response=expect_response, log=log)
        
        if not success:
            target = Target() #Create empty target

        self.HLC.set_target(target)

        if expect_response:
            response = success
            self.send_data(response)

    def command_set_planner(self, planner, expect_response = False, log = False):
        success = super().command_set_planner(planner, expect_response, log)
 
        if success:
            self.HLC.set_trajectory_planner(planner(self.HLC)) #Make sure planner initialises

        if expect_response:
            response = type(self.HLC.trajectory_planner)
            self.send_data(response)

    def command_set_speed_limit(self, speed_limit, expect_response = True, log = False):
        success = super().command_set_speed_limit(speed_limit, expect_response, log)

        if success:
            self.HLC.config.linear_velocity_max = speed_limit

        if expect_response:
            response = self.HLC.config.linear_velocity_max
            self.send_data(response)

    def command_set_acceleration_limit(self, acceleraton_limit, expect_response = True, log = False):
        success = super().command_set_acceleration_limit(acceleraton_limit, expect_response, log)

        if success:
            self.HLC.config.acceleration_max = acceleraton_limit

        if expect_response:
            response = self.HLC.config.acceleration_max
            self.send_data(response)

    def command_reset_localisation(self, expect_response = False, log = False):
        success = super().command_reset_localisation(expect_response=expect_response, log=log)

        if success:
            self.HLC.localisation.reset_localisation()

        if expect_response:
            response = success
            self.send_data(response)

    def command_get_location(self, expect_response = True, log = False):
        super().command_get_location(log=log)
        
        location: VelocityPose = self.HLC.localisation.current_pose
        if location == None:
            print("Odom report failed")
        else:
            if log:
                print(location)
        if expect_response:
            response = location
            self.send_data(response)

    def command_custom(self, expect_response = False, log = False):
        success = super().command_custom(log=log)
        if self.custom_function is None:
            success = False
        if not success:
            print("Custom function failed")
            return False
        print(f"Custom Command Rec: {time.time()}")
        self.custom_function(self.HLC)

if __name__ == "__main__":
    pass