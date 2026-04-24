import gymnasium as gym
import pandas as pd
import envs
import numpy as np
import sys
import matplotlib.pyplot as plt

R_0_means = np.loadtxt("R_0_means.txt")
R_1_means = np.loadtxt("R_1_means.txt")
R_2_means = np.loadtxt("R_2_means.txt")
R_3_means = np.loadtxt("R_3_means.txt")
R_4_means = np.loadtxt("R_4_means.txt")

R_0_means = R_0_means[:26]
R_1_means = R_1_means[:26]
R_2_means = R_2_means[:26]
R_3_means = R_3_means[:26]
R_4_means = R_4_means[:26]


R_max_means = np.maximum.reduce([R_0_means, R_1_means, R_2_means, R_3_means, R_4_means])

rs_axes = plt.subplots(1,1, figsize = (10,10))[1]
rs_axes.plot(R_0_means, lw=2, marker='.', color="black", label='Rs (azimuth +0.00)')
rs_axes.plot(R_1_means, lw=2, marker='.', color="blue", label='Rs (azimuth +0.01)')
rs_axes.plot(R_2_means, lw=2, marker='.', color="green", label='Rs (azimuth +0.02)')
rs_axes.plot(R_3_means, lw=2, marker='.', color="red", label='Rs (azimuth +0.03)')
rs_axes.plot(R_4_means, lw=2, marker='.', color="magenta", label='Rs (azimuth +0.04)')
rs_axes.plot(R_max_means, lw=2, marker='.', color="violet", label='Maximun pointwise RS')
rs_axes.set_xlabel('Time (seconds)')
rs_axes.set_ylabel('Secrecy Rate')
rs_axes.set_title('Bob Secrecy Rate')
plt.legend()
plt.savefig('SecrecyRate2.png')
plt.show()





