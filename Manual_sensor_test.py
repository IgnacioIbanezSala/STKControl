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
C_no_sensor = []
C_no_no_sensor = []
Eb_no_sensor = []
Eb_no_no_sensor = []
for i in range(span):
    
    idx_sc1a = df_sc1a.index[df_sc1a["Time"] == df_sc1a_manual.at[i, "Time"]]
    if idx_sc1a.empty:
        pass
    else:
        C_no_sensor.append(df_sc1a.loc[idx_sc1a]["C/No"])
        C_no_no_sensor.append(df_sc1a_manual.loc[i]["C/No"])
        Eb_no_sensor.append(df_sc1a.loc[idx_sc1a]["Eb/No"])
        Eb_no_no_sensor.append(df_sc1a_manual.loc[i]["Eb/No"])
        error.append((df_sc1a.loc[idx_sc1a]["C/No"]-df_sc1a_manual.loc[i]["C/No"]))
                
error_graph = plt.subplots(1,1)[1]
error_graph.plot(error)
plt.title('Quadratic Error Measurement')
plt.ylabel('Error magnitude')
plt.legend()
plt.show()


print('Mean error: ', np.mean(error))

range_graph = plt.subplots(1,2)[1]

range_graph[0].plot(C_no_sensor, color="blue", label='C/No sensor', marker='o', ls='--')
range_graph[0].plot(C_no_no_sensor, color="orange", label='C/No no sensor', marker='x', ls=(0, (5, 10)))
range_graph[0].set_title("C/No comprarision between manual and automatic antenna pointing")
range_graph[0].set_ylabel('C/No [dB]')
range_graph[0].set_xlabel('Simulation Step')
range_graph[0].legend()

range_graph[1].plot(Eb_no_sensor, color="blue", label='Eb/No sensor', marker='o', ls='--')
range_graph[1].plot(Eb_no_no_sensor, color="orange", label='Eb/No no sensor', marker='x', ls=(0, (5, 10)))
range_graph[1].set_title("Eb/No comprarision between manual and automatic antenna pointing")
range_graph[1].set_ylabel('Eb/No [dB]')
range_graph[1].set_xlabel('Simulation Step')
range_graph[1].legend()

plt.tight_layout()
plt.show()