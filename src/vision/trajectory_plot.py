import trajectory_estimation
import json
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

def plot_quad_vs_linear(time, z_measured, z_linear):
    """Plot the linear and measured quadratic points"""
    fig = plt.figure()
    ax2 = plt.axes()
    ax2.scatter(time,z_measured, label= "Measured Quadratic Path")
    ax2.scatter(time,z_linear, label = "Linear Estimation")
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Ball height (m)')
    ax2.legend()




if __name__ == "__main__":
    #Load Data
    filename = "vision/log/90fpsiback.json"
    with open(filename, "r") as file:
            data = json.load(file)
    print(f"Datapoints: {len(data)}")
    tests = [3,7,17]
    colours = ["red", "blue", "green", "orange", "magenta"]
    estimator = trajectory_estimation.TrajectoryEstimator()
    initial_time = data[0]["timestamp"]
    #For given number of samples


       

    x_m = []
    y_m = []
    z_m = []
    t_m = []
    z_m_lin = []

    #plot measured points
    g = -9.81
    for point in data:
        x_m.append(point["x"])
        y_m.append(point["y"])
        z_m.append(point["z"])
        time = point["timestamp"]-initial_time
        t_m.append(time)
        z_m_lin.append(point["z"]-0.5*g*(time)**2)

    plot_quad_vs_linear(t_m, z_m, z_m_lin) #Plots a graph showing linearisation for prediction
    
    #plot
    fig = plt.figure()
    ax = plt.axes(projection='3d') 
    ax.scatter3D(x_m, y_m, z_m, color = "black", marker = 'x', label = "Measured points")
    index = 0
    for test in tests:
        while len(estimator.positon_array) != test:
            datum = data[index]
            index +=1
            point = trajectory_estimation.TrajectoryPoint(datum["x"], datum["y"],datum["z"], datum["timestamp"] )
            estimator.add_point(point)
        #Generate Prediction
        x_p = []
        y_p = []
        z_p = []
        times_s = []
        times_ms= range(0,int(estimator.get_impact_point(True).timestamp*1000))
        for ms in times_ms:
            times_s.append(float(ms)/1000)
        
        for time in times_s:
            predicted_point = estimator.trajectory.get_pos_at_throw_time(time)
            x_p.append(predicted_point.x)
            y_p.append(predicted_point.y)
            z_p.append(predicted_point.z)
        
        impact = estimator.get_impact_point()
                
        colour = colours.pop()
        ax.scatter3D([impact.x], [impact.y], [impact.z], color = colour, marker = 'o')
        ax.plot3D(x_p, y_p, z_p, color = colour, label = f"Prediction from {test} points")

    ax.legend()
    ax.set_xlim(-1, 3)
    ax.set_ylim(-2, 2)
    ax.set_zlim(0, 2)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.show()
    