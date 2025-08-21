import gymnasium as gym
import pandas as pd
import envs

#env = gym.make("STKEnv-v0", scenario_filename = "C:/Users/isnac/OneDrive/Escritorio/Programas/Python/STKControl/Scenarios/Spy_Sat_manualpointing.json")
env = envs.StkEnv("C:/Users/isnac/OneDrive/Escritorio/Programas/Python/STKControl/Scenarios/Spy_Sat_manualpointing.json")

env.reset()

df = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")

action1 = df['Azimuth'].to_list()
action2 = df['Elevation'].to_list()

obs = []

truncated = terminated = False

for a1, a2 in zip(action1, action2):
    obs, reward, terminated, truncated, info = env.step([a1,a2])
    print(obs)
    if terminated:
        break
