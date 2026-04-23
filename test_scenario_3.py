import gymnasium as gym
import pandas as pd
import envs
import numpy as np
import sys

#env = gym.make("STKEnv-v0", scenario_filename = "C:/Users/isnac/OneDrive/Escritorio/Programas/Python/STKControl/Scenarios/Spy_Sat_manualpointing.json")
env = envs.StkEnv("Scenarios/Spy_Sat_manualpointing.json")

obs=env.reset()

df = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")

action1 = df['Azimuth'].to_list()
action2 = df['Elevation'].to_list()

#obs = []

truncated = terminated = False

a1=0
a2=0


actions1= np.linspace(-1,1,3)
actions2= np.linspace(-1,1,3)
R=np.zeros([actions1.size,actions2.size])





N=760 # duracion de la pasada 766 steps
N=10
R=np.zeros([N,5])

obs=env.reset()
for n in range(N): # duracion de la pasada 766 steps
    obs, reward, terminated, truncated, info = env.step([0,0.0937])
    R[n,0]=reward[1]
    if (n%(N//2)) == 0 : 
        print("n",n)
print ("--",reward)
print()

reporte = pd.DataFrame(info['bob_obs_table'])
reporte.to_excel("Reports/EnvBobLog_0_deg.xlsx")

reporte = pd.DataFrame(info['eve_obs_table'])
reporte.to_excel("Reports/EnvEveLog_0_deg.xlsx")      
   

exit()   
obs=env.reset()       
for n in range(N): # duracion de la pasada 766 steps
    obs, reward, terminated, truncated, info = env.step([0.01,0])
    R[n,1]=reward[1]
    if (n%(N//2)) == 0 : 
        print("n",n)





obs=env.reset()
for n in range(N): # duracion de la pasada 766 steps
    obs, reward, terminated, truncated, info = env.step([0.02,0])
    R[n,2]=reward[1]
    if (n%(N//2)) == 0 : 
        print("n",n)    
        
obs=env.reset()
for n in range(N): # duracion de la pasada 766 steps
    obs, reward, terminated, truncated, info = env.step([0.03,0])
    R[n,3]=reward[1]
    if (n%(N//2)) == 0 : 
        print("n",n)    
        
obs=env.reset()
for n in range(N): # duracion de la pasada 766 steps
    obs, reward, terminated, truncated, info = env.step([0.04,0])
    R[n,4]=reward[1]
    if (n%(N//2)) == 0 : 
        print("n",n)    
        
print ("column 1")
print (R[:,0] < R[:,1])
print ("column 2")
print (R[:,0] < R[:,2])
print ("column 3")
print (R[:,0] < R[:,3])
print ("column 4")
print (R[:,0] < R[:,4])

rs_axes = plt.subplots(1,1, figsize = (10,10))[1]
rs_axes.plot(R[:,1], lw=2, marker='.', color="blue", label='Rs (azimuth +0.01)')
rs_axes.plot(R[:,2], lw=2, marker='.', color="green", label='Rs (azimuth +0.02)')
rs_axes.plot(R[:,3], lw=2, marker='.', color="red", label='Rs (azimuth +0.03)')
rs_axes.plot(R[:,4], lw=2, marker='.', color="magenta", label='Rs (azimuth +0.04)')
rs_axes.set_xlabel('Time (seconds)')
rs_axes.set_ylabel('Secrecy Rate')
rs_axes.set_title('Bob Secrecy Rate')
plt.legend()
plt.savefig('SecrecyRate2.png')
plt.show()

print(R)
exit()

for i,a1 in enumerate(actions1):
 for j,a2 in enumerate(actions2):
  #obs=env.reset()
  obs, reward, terminated, truncated, info = env.step([0,0])
  R[i,j]=reward[1]
print("reward 0 pointing",reward_reset) 
print(R)
print (R>reward_reset[1])
flat_index=np.argmax(R)
row_index, col_index = np.unravel_index(flat_index, R.shape)
print("arg Rmax",row_index, col_index)
#print(obs,"reward =",reward)
reporte = pd.DataFrame(info['bob_obs_table'])
reporte.to_excel("Reports/EnvBobLog_1.xlsx")
#reporte.to_csv("Reports/EnvBobLog.csv")

reporte = pd.DataFrame(info['eve_obs_table'])
reporte.to_excel("Reports/EnvEveLog_1.xlsx")
#reporte.to_csv("Reports/EnvEveLog.csv")


#env.reset()