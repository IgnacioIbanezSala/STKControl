import numpy as np
import scipy as sp
from scipy import stats
from math import log2, log, sqrt
import matplotlib.pyplot as plt
import pandas as pd



df_eve = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")
df_sc1a = pd.read_excel("Reports/SAOCOM1A_transmitterCBA.xlsx")

span = min(len(df_eve["Range"]), len(df_sc1a["Range"]))
error = []
sat_distance = []

for i in range(span):
    
    idx_sc1a = df_sc1a.index[df_sc1a["Time"] == df_eve.at[i, "Time"]]
    if idx_sc1a.empty:
        pass
    else:
        x_diff = df_sc1a.loc[idx_sc1a]["x"] - df_eve.loc[i]["x"]
        y_diff = df_sc1a.loc[idx_sc1a]["y"] - df_eve.loc[i]["y"]
        z_diff = df_sc1a.loc[idx_sc1a]["z"] - df_eve.loc[i]["z"]
        distance = sqrt(x_diff**2+y_diff**2+z_diff**2)
        sat_distance.append(distance)
                
distance_graph = plt.subplots(1,1)[1]
distance_graph.plot(sat_distance)
plt.show()

"""
print('Mean error: ', np.mean(error))

range_graph = plt.subplots(1,1)[1]
range_graph.plot(range_sensor, color="blue")
range_graph.plot(range_no_sensor, color="orange")
plt.show()
"""