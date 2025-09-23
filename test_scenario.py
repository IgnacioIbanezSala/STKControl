import gymnasium as gym
import pandas as pd
import envs

#env = gym.make("STKEnv-v0", scenario_filename = "C:/Users/isnac/OneDrive/Escritorio/Programas/Python/STKControl/Scenarios/Spy_Sat_manualpointing.json")
env = envs.StkEnv("Scenarios/Spy_Sat_manualpointing.json")

env.reset()

df = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")

action1 = df['Azimuth'].to_list()
action2 = df['Elevation'].to_list()

obs = []

truncated = terminated = False

i = 0
for a1, a2 in zip(action1, action2):
    obs, reward, terminated, truncated, info = env.step([1,0])
    print(obs)
    i += 1
    if terminated or i == 25:
        break

reporte = pd.DataFrame(info['bob_obs_table'])
reporte.to_excel("Reports/EnvBobLog.xlsx")
reporte.to_csv("Reports/EnvBobLog.csv")

reporte = pd.DataFrame(info['eve_obs_table'])
reporte.to_excel("Reports/EnvEveLog.xlsx")
reporte.to_csv("Reports/EnvEveLog.csv")


env.reset()