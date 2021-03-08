from rp1controller import Target
import rp1controller
import socket, pickle
import rp1controller
import time, threading


IP_laptop = "192.168.137.1"

def reset_target():
    while(True):
        delay = time.time()-time_last
        if ((delay)>2 and not first):
            print(f"Reset {delay} at {time.time()}")
            target = Target()
            HLC.set_target(target)
            time_last = time.time()


target = Target()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((socket.gethostname(), 1066))
s.connect((IP_laptop, 1066))
HLC = rp1controller.RP1Controller()

time_last = time.time()
watchdog = threading.Thread(target=reset_target)
watchdog.start()
first = True

while True:
    msg = s.recv(1024)
    time_last = time.time()
    try: 
        target: Target = pickle.loads(msg)
    except:
        target = Target()
    first = False
    HLC.set_target(target)