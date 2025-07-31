import numpy as np
import scipy as sp
from scipy import stats
from math import log2, log, sqrt
import matplotlib.pyplot as plt
import pandas as pd
import Channel
import Secrecy_Rates as sr


df_sc1a = pd.read_excel("Reports/SAOCOM1A_transmitterCBA.xlsx")
df_sc1a_manual = pd.read_excel("Reports/SAOCOM1A_transmitterCBAmanual_antena_pointing.xlsx")


span = min(len(df_sc1a_manual["Range"]), len(df_sc1a["Range"]))
error = []
range_sensor = []
range_no_sensor = []
for i in range(span):
    
    idx_sc1a = df_sc1a.index[df_sc1a["Time"] == df_sc1a_manual.at[i, "Time"]]
    if idx_sc1a.empty:
        pass
    else:
        range_sensor.append(df_sc1a.loc[idx_sc1a]["C/No"])
        range_no_sensor.append(df_sc1a_manual.loc[i]["C/No"])
        error.append((df_sc1a.loc[idx_sc1a]["C/No"]-df_sc1a_manual.loc[i]["C/No"]))
                
error_graph = plt.subplots(1,1)[1]
error_graph.plot(error)
plt.show()


print('Mean error: ', np.mean(error))

range_graph = plt.subplots(1,1)[1]
range_graph.plot(range_sensor, color="blue")
range_graph.plot(range_no_sensor, color="orange")
plt.show()