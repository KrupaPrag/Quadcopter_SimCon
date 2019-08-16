# -*- coding: utf-8 -*-
"""
author: John Bass
email: john.bobzwik@gmail.com
license: MIT
Please feel free to use and modify this, but keep the above information. Thanks!
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import cProfile

from trajectory import Trajectory
from ctrl import Control
from quadFiles.quad import Quadcopter
from utils.windModel import Wind
import utils
import config

def quad_sim(t, Ts, quad, ctrl, wind, traj):
    
    # Trajectory for Desired States
    # ---------------------------
    sDes = traj.desiredState(t, quad)        
    
    # Generate Commands
    # ---------------------------
    ctrl.controller(quad, sDes, Ts, traj)

    # Dynamics
    # ---------------------------
    quad.update(t, Ts, ctrl.w_cmd, wind)


def main():
    start_time = time.time()

    # Simulation Setup
    # --------------------------- 
    Ti = 0
    Ts = 0.005
    Tf = 16

    # Choose trajectory settings
    # --------------------------- 
    ctrlOptions = ["xyz_pos", "xy_vel_z_pos", "xyz_vel"]
    trajSelect = np.ones(3)

    # Select Control Type             (0: xyz_pos,         1: xy_vel_z_pos,          2: xyz_vel)
    ctrlType = ctrlOptions[0]   
    # Select Position Trajectory Type (0: hover,           1: pos_waypoint_timed,    2: pos_waypoint_interp,    3: minimum velocity
    #                                  4: minimum accel,   5: minimum jerk,          6: minimum snap
    trajSelect[0] = 3           
    # Select Yaw Trajectory Type                          (1: yaw_waypoint_timed,    2: yaw_waypoint_interp)
    trajSelect[1] = 2           
    # Select if waypoint time is used, or if average speed is used to calculate waypoint time   (0: waypoint time,   1: average speed)
    trajSelect[2] = 0           
    print("Control type: {}".format(ctrlType))

    # Initialize Quadcopter, Controller, Wind, Result Matrixes
    # ---------------------------
    quad = Quadcopter(Ti)
    traj = Trajectory(ctrlType, trajSelect)
    ctrl = Control(quad, traj.yawType)
    wind = Wind('None', 2.0, 90, -15)

    t_all     = Ti
    s_all     = quad.state.T
    pos_all   = quad.pos.T
    vel_all   = quad.vel.T
    quat_all  = quad.quat.T
    omega_all = quad.omega.T
    euler_all = quad.euler.T
    sDes_all  = ctrl.sDesCalc.T
    w_cmd_all = ctrl.w_cmd.T
    wMotor_all= quad.wMotor.T
    thr_all   = quad.thr.T
    tor_all   = quad.tor.T

    # Run Simulation
    # ---------------------------
    t = Ti
    i = 0
    while round(t,3) < Tf:
        
        quad_sim(t, Ts, quad, ctrl, wind, traj)
        t += Ts

        # print("{:.3f}".format(t))
        t_all     = np.vstack((t_all, t))
        s_all     = np.vstack((s_all, quad.state.T))
        pos_all   = np.vstack((pos_all, quad.pos.T))
        vel_all   = np.vstack((vel_all, quad.vel.T))
        quat_all  = np.vstack((quat_all, quad.quat.T))
        omega_all = np.vstack((omega_all, quad.omega.T))
        euler_all = np.vstack((euler_all, quad.euler.T))
        sDes_all  = np.vstack((sDes_all, ctrl.sDesCalc.T))
        w_cmd_all = np.vstack((w_cmd_all, ctrl.w_cmd.T))
        wMotor_all= np.vstack((wMotor_all, quad.wMotor.T))
        thr_all   = np.vstack((thr_all, quad.thr.T))
        tor_all   = np.vstack((tor_all, quad.tor.T))
        i += 1
    
    end_time = time.time()
    print("Simulated {:.2f}s in {:.6f}s.".format(t, end_time - start_time))

    # View Results
    # ---------------------------
    utils.makeFigures(quad.params, t_all, pos_all, vel_all, quat_all, omega_all, euler_all, w_cmd_all, wMotor_all, thr_all, tor_all, sDes_all)
    ani = utils.sameAxisAnimation(t_all, pos_all, quat_all, Ts, quad.params)
    plt.show()

if __name__ == "__main__":
    if (config.orient == "NED" or config.orient == "ENU"):
        main()
        # cProfile.run('main()')
    else:
        raise Exception("{} is not a valid orientation. Verify config.py file.".format(config.orient))