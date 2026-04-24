import gymnasium as gym
import pandas as pd
import envs
import numpy as np
import sys
import matplotlib.pyplot as plt

#env = gym.make("STKEnv-v0", scenario_filename = "C:/Users/isnac/OneDrive/Escritorio/Programas/Python/STKControl/Scenarios/Spy_Sat_manualpointing.json")
env = envs.StkEnv("Scenarios/Spy_Sat_manualpointing.json")

obs=env.reset()

df = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")

action1 = df['Azimuth'].to_list()
action2 = df['Elevation'].to_list()

truncated = terminated = False


actions1= np.linspace(-1,1,3)
actions2= np.linspace(-1,1,3)
R=np.zeros([actions1.size,actions2.size])


N=25
R=np.zeros([N,5])
rollouts = 100
R_0 = []
R_1 = []
R_2 = []
R_3 = []
R_4 = []

for r in range(rollouts):
    obs=env.reset()
    for n in range(N): 
        obs, reward, terminated, truncated, info = env.step([0,0])
        R[n,0]=reward[1]
        if terminated:
            break

    R_0.append(R[:,0])
    print()

    obs=env.reset()       
    for n in range(N): 
        obs, reward, terminated, truncated, info = env.step([0.01,0])
        R[n,1]=reward[1]
        if terminated:
            break

    R_1.append(R[:,1])        

    obs=env.reset()
    for n in range(N): 
        obs, reward, terminated, truncated, info = env.step([0.02,0])
        R[n,2]=reward[1]
        if terminated:
           break

    R_2.append(R[:,2])

    obs=env.reset()
    for n in range(N): 
        obs, reward, terminated, truncated, info = env.step([0.03,0])
        R[n,3]=reward[1]
        if terminated:
            break    

    R_3.append(R[:,3])


    obs=env.reset()
    for n in range(N): 
        obs, reward, terminated, truncated, info = env.step([0.04,0])
        R[n,4]=reward[1]
        if terminated:
            break

    R_4.append(R[:,4]) 
    print ("Rollout -- ", r)

        
print ("column 1")
print (R[:,0] < R[:,1])
print ("column 2")
print (R[:,0] < R[:,2])
print ("column 3")
print (R[:,0] < R[:,3])
print ("column 4")
print (R[:,0] < R[:,4])


R_0_means = np.median(R_0, axis=0)
R_1_means = np.median(R_1, axis=0)
R_2_means = np.median(R_2, axis=0)
R_3_means = np.median(R_3, axis=0)
R_4_means = np.median(R_4, axis=0)

np.savetxt('R_0_means.txt', R_0_means, fmt='%f')
np.savetxt('R_1_means.txt', R_1_means, fmt='%f')
np.savetxt('R_2_means.txt', R_2_means, fmt='%f')
np.savetxt('R_3_means.txt', R_3_means, fmt='%f')
np.savetxt('R_4_means.txt', R_4_means, fmt='%f')


rs_axes = plt.subplots(1,1, figsize = (10,10))[1]
rs_axes.plot(R_0_means, lw=2, marker='.', color="black", label='Rs (azimuth +0.00)')
rs_axes.plot(R_1_means, lw=2, marker='.', color="blue", label='Rs (azimuth +0.01)')
rs_axes.plot(R_2_means, lw=2, marker='.', color="green", label='Rs (azimuth +0.02)')
rs_axes.plot(R_3_means, lw=2, marker='.', color="red", label='Rs (azimuth +0.03)')
rs_axes.plot(R_4_means, lw=2, marker='.', color="magenta", label='Rs (azimuth +0.04)')
rs_axes.set_xlabel('Time (seconds)')
rs_axes.set_ylabel('Secrecy Rate')
rs_axes.set_title('Bob Secrecy Rate')
plt.legend()
plt.savefig('SecrecyRate2.png')
plt.show()

print(R)
exit()

