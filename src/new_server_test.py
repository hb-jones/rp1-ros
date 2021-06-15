from rp1controller import Target
from rp1controller.trajectory_planners import LocalVelocityControl
from rp1controller import RP1Server
from time import sleep

ip = "192.168.137.1"

print()
print("T - Starting Server")

server = RP1Server(ip)

sleep(10) #TODO add check ready

print("T - Starting test Sequence")

test_target = Target()
test_planner = LocalVelocityControl
test_speed_limit = 1.2
test_accel = 0.3

test_speeds = [(0,0),(1,0),(1,1),(0,0),(1,0),(1,1),(0,0),(1,0),(1,1),(0,0)]

if server.command_set_speed_limit(test_speed_limit, expect_response=True, log=True):
    print("T - Speed limit updated successfully")
else:
    print("T - Speed limit update failed")
sleep(2)

if server.command_set_acceleration_limit(test_accel, expect_response=True, log=True):
    print("T - Accel limit updated successfully")
else:
    print("T - Accel limit update failed")
sleep(2)

if server.command_reset_localisation(expect_response=True, log=True):
    print("T - Localisation Reset")
else:
    print("T - Localisation Reset Failed")
sleep(2)

if server.command_set_planner(test_planner, expect_response=True, log=True):
      print("T - Planner Updated")
else:
    print("T - Planner Update Failed")
sleep(2)

for speed in test_speeds:
    test_target.local_velocity = speed
    server.command_set_target(test_target)
    sleep(2)

print("T - Testing rapid target changes")
sleep(3)

for i in range(1,100):
    speed = (i/50,0)
    test_target.local_velocity = speed
    server.command_set_target(test_target)
    sleep(0.02)

print("T - Inital Test Complete - testing watchdog")
test_target.local_velocity = (1,0)
server.command_set_target(test_target)
server.watchdog_delay=5


sleep(10)
server.command_set_target(Target())
del server

print("Test Sequence Complete")
print()




