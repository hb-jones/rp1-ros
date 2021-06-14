from rp1controller import Target
from rp1controller.trajectory_planners import LocalVelocityControl
from rp1controller import RP1Server
from time import sleep

ip = "192.168.137.1"

print()
print("Starting Server")

server = RP1Server(ip)

sleep(10) #TODO add check ready

print("Starting test Sequence")

test_target = Target()
test_planner = LocalVelocityControl
test_speed_limit = 1.2
test_accel = 0.3

test_speeds = [(0,0),(1,0),(1,1),(0,0),(1,0),(1,1),(0,0),(1,0),(1,1),(0,0)]

server.command_set_speed_limit(test_speed_limit, expect_response=True, log=True)
sleep(0.5)

server.command_set_acceleration_limit(test_accel, expect_response=True, log=True)
sleep(0.5)

server.command_reset_localisation(expect_response=True, log=True)
sleep(0.5)

server.command_set_planner(test_planner, expect_response=True, log=True)
sleep(0.5)

for speed in test_speeds:
    test_target.local_velocity = speed
    server.command_set_target(test_target)
    sleep(2)

print("Inital Test Complete - testing watchdog")

server.watchdog_delay=5

server.command_set_target(Target())
sleep(1)

del server

print("Test Sequence Complete")
print()




