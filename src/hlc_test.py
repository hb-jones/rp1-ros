import rp1controller
from rp1controller import Target
from time import sleep


#Test script to find problem class

hlc = rp1controller.RP1Controller()
#hlc.localisation.loop_run_flag = False

t0 = Target((0,0),0)
t1 = Target((1,0),0)
t2 = Target((0,-0.5),0)
delay = 1

hlc.set_target(t1)
sleep(delay)
hlc.set_target(t2)
sleep(delay)
hlc.set_target(t1)
sleep(delay)
hlc.set_target(t2)
sleep(delay)
hlc.set_target(t1)
sleep(delay)
hlc.set_target(t2)
sleep(delay)
hlc.set_target(t1)
sleep(delay)

for i in range(0,1000):
    sleep(0.05)
    hlc.set_target(t1)
    sleep(0.05)
    hlc.set_target(t2)

hlc.set_target(t0)
