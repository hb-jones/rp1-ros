import rp1controller
from rp1controller import low_level_interface
import time
class DummyController:
    def __init__(self):
        from rp1controller import rp1config
        self.config = rp1config.RP1Configuration()
        return


hlc = DummyController()

lli = low_level_interface.LowLevelInterface(hlc)
lli.start_loop()

delay = 1

time.sleep(delay)
lli.set_target((1,0),0)
time.sleep(delay)
lli.set_target((0,0),0)
time.sleep(delay)
lli.set_target((1,0),0)
time.sleep(delay)
lli.set_target((0,0),0)
time.sleep(delay)
lli.set_target((1,0),0)

for i in range (0,1000):
    time.sleep(0.01)
    lli.set_target((1,0),0)
    time.sleep(0.01)
    lli.set_target((0,1),0)
lli.set_target((0,0),0)
time.sleep(delay)

lli.stop_loop()