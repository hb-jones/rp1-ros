import rp1controller
from rp1controller.low_level_interface import get_single_target
from time import sleep
hlc = rp1controller.RP1Controller()
lli = hlc.low_level_interface

target = get_single_target("axis_FL",2)
print("Testing FL")
lli.set_motor_target_direct(target)
sleep(5)

target = get_single_target("axis_FR",2)
print("Testing FR")
lli.set_motor_target_direct(target)
sleep(5)

target = get_single_target("axis_BL",2)
print("Testing BL")
lli.set_motor_target_direct(target)
sleep(5)

target = get_single_target("axis_BR",2)
print("Testing BR")
lli.set_motor_target_direct(target)
sleep(5)

target = get_single_target("axis_FL", 0)
lli.set_motor_target_direct(target)

