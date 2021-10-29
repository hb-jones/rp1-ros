from rp1controller import RP1Controller, Target
from rp1controller.trajectory_planners import WorldPoseControl

robot_platform = RP1Controller()                            #Initialise the robot platform
robot_platform.set_trajectory_planner(WorldPoseControl)     #Set the desired planner
target_position = Target()                                  #Create a target and set the target position
target_position.world_point = (1,0)
robot_platform.set_target(target_position)                  #Command the platform to move to the target


