import odrive
import time
import math
import threading




import rp1controller
from rp1controller import Target

HLC = rp1controller.RP1Controller()

time.sleep(0.1)
target = Target((1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((-1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((-1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((-1,0),0)
HLC.low_level_interface.set_target(target)

time.sleep(2)
target = Target((0,0),0)
HLC.low_level_interface.set_target(target)


# thread_active = True

# serial_a = "208239904D4D" #String containing front ODrive's serial number in hex format all capitals
# serial_b = "206039994D4D" #String containing back  ODrive's serial number in hex format all capitals

# odrv = odrive.find_any(serial_number=serial_a)
# odrv_b= odrive.find_any(serial_number=serial_b)
# axis = odrv.axis0
# axis_thread = odrv.axis0

# def thread_test():
#     x=1
#     loops = 0
#     thread_start_time = time.perf_counter()
#     while thread_active:
#         x=1
#         axis_thread.controller.input_vel = x
#         measured = axis_thread.controller.input_vel
#         x=2
#         axis_thread.controller.input_vel = x
#         measured = axis_thread.controller.input_vel
#         loops+=2
#     thread_average_time_taken = (time.perf_counter()-thread_start_time)/loops
#     print(f"Thread performed {loops} loops with average of {thread_average_time_taken}s")





# print()
# print()
# print()
# x = 1
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()

# x = -1
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()

# x = 1.1
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()

# x = 1.0000001
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()

# x = 2.314141525321241513523253415623542783542678542678354254254267354
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()

# x = math.pi
# start = time.perf_counter()
# axis.controller.input_vel = x
# taken = time.perf_counter()-start
# print(f"Time taken for x: {x} is: {taken}s")
# start = time.perf_counter()
# measured = axis.controller.input_vel
# taken = time.perf_counter()-start
# print(f"Time taken to measure val: {measured} is: {taken}s")
# print()


# start = time.perf_counter()
# for i in range(1000):
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel
# taken = (time.perf_counter()-start)/2000
# print(f"Average time taken 1000 loops is: {taken}s")
# print() 

# thread = threading.Thread(target=thread_test)
# thread.start()
# start = time.perf_counter()
# for i in range(1000):
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel
# taken = (time.perf_counter()-start)/2000
# thread_active = False
# thread.join()
# print(f"Average time taken 1000 loops with obstruction thread is: {taken}s")
# print()

# thread_active = True
# axis_thread = odrv.axis1
# thread = threading.Thread(target=thread_test)
# thread.start()
# start = time.perf_counter()
# for i in range(1000):
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel
# taken = (time.perf_counter()-start)/2000
# thread_active = False
# thread.join()
# print(f"Average time taken 1000 loops with obstruction thread is: {taken}s")
# print()


# axis_thread = odrv_b.axis0
# thread_active = True
# thread = threading.Thread(target=thread_test)
# thread.start()
# start = time.perf_counter()
# for i in range(1000):
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel
# taken = (time.perf_counter()-start)/2000
# thread_active = False
# thread.join()
# print(f"Average time taken 1000 loops with obstruction thread on other drive is: {taken}s")
# print()


# start = time.perf_counter()
# for i in range(1000):
#     axis = odrv.axis0
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv_b.axis0
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv.axis1
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv_b.axis1
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

# taken = (time.perf_counter()-start)/8000
# print(f"Average time taken 1000 changing drive loops is: {taken}s")
# print() 


# start = time.perf_counter()
# for i in range(1000):
#     axis = odrv.axis0
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv.axis1
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv_b.axis0
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

#     axis = odrv_b.axis1
#     axis.controller.input_vel = i/1000
#     measured = axis.controller.input_vel

# taken = (time.perf_counter()-start)/8000
# print(f"Average time taken 1000 changing drive loops alternative order is: {taken}s")
# print() 






# print()
# print()