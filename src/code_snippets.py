from typing import Tuple


class Target:
    local_velocity = (0,0)      #Linear velocity in local frame (m/s)
    angular_velocity  = 0       #Angular velocity (rad/s)
    world_velocity = (0,0)      #Linear velocity target in world frame (m/s)
    world_bearing  = 0          #Bearing to face (rad)
    world_point = (0,0)         #Coordinate to move to (m)
    world_point_facing = (0,0)  #Coordinate for platform to face (m)
    
    def __init__(self, local_velocity: Tuple[float, float] = (0,0), local_angular: float = 0):
        self.local_velocity = local_velocity
        self.angular_velocity  = local_angular
        return 

    def __str__(self):
        return f"Local Velocity: {self.local_velocity}, Angular: {self.angular_velocity}, Position: {self.world_point}, Bearing: {self.world_bearing}"
    


class VelocityPose: 
    timestamp = 0               #Timestamp (s)
    local_velocity = (0,0)      #Linear velocity in local frame (m/s)
    angular_velocity  = 0       #Angular velocity (rad/s)
    world_velocity = (0,0)      #Linear velocity in world frame (m/s)
    world_heading  = 0          #Heading (rad)
    world_position = (0,0)      #Position in world (m)


    def __init__(self):
        pass

    def __str__(self): #TODO maybe not this?
        return f"{self.timestamp}, {self.world_x_position}, {self.world_y_position}, {self.heading}, {self.local_x_velocity}, {self.local_y_velocity}, {self.angular_velocity}"






x = Target()
y = Target()

x.world_velocity = (1,1)
print(x.world_velocity)
print(y.world_velocity)
print()
Target.world_velocity = (2,2)
print(x.world_velocity)
print(y.world_velocity)
print()