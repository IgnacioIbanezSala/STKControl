import numpy as np
import scipy as sp
from scipy import stats
from math import log2, log, sqrt
import matplotlib.pyplot as plt
import pandas as pd



df_sc1a = pd.read_excel("Reports/SAOCOM1A_transmitterCBA.xlsx")
df_eve = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")


span = min(len(df_eve["Range"]), len(df_sc1a["Range"]))
error = []
C_no_sc1a = []
C_no_eve = []
Eb_no_sc1a = []
Eb_no_eve = []
Xmtr_gain_sc1a = []
Xmtr_gain_eve = []
range_sc1a = []
range_eve = []
elevation_eve = []
for i in range(span):
    
    idx_sc1a = df_sc1a.index[df_sc1a["Time"] == df_eve.at[i, "Time"]]
    if idx_sc1a.empty:
        pass
    else:
        C_no_sc1a.append(df_sc1a.loc[idx_sc1a]["C/No"])
        C_no_eve.append(df_eve.loc[i]["C/No"])
        Eb_no_sc1a.append(df_sc1a.loc[idx_sc1a]["Eb/No"])
        Eb_no_eve.append(df_eve.loc[i]["Eb/No"])
        Xmtr_gain_sc1a.append(df_sc1a.loc[idx_sc1a]["Xmtr Gain"])
        Xmtr_gain_eve.append(df_eve.loc[i]["Xmtr Gain"])
        range_sc1a.append(df_sc1a.loc[idx_sc1a]["Range"])
        range_eve.append(df_eve.loc[i]["Range"])
        elevation_eve.append(df_eve.loc[i]["Xmtr Elevation"])
        error.append((df_sc1a.loc[idx_sc1a]["C/No"]-df_eve.loc[i]["C/No"]))
                
error_graph = plt.subplots(1,1)[1]
error_graph.plot(error)
plt.title('Quadratic Error Measurement')
plt.ylabel('Error magnitude')
plt.legend()
plt.show()


print('Mean error: ', np.mean(error))

range_graph = plt.subplots(3,2)[1]

range_graph[0][0].plot(C_no_sc1a, color="blue", label='C/No SC1A', ls='--')
range_graph[0][0].plot(C_no_eve, color="orange", label='C/No Eve', marker='x', ls=(0, (5, 10)))
range_graph[0][0].set_title("C/No comprarision between SC1A and Eve")
range_graph[0][0].set_ylabel('C/No [dB]')
range_graph[0][0].set_xlabel('Simulation Step')
range_graph[0][0].legend()

range_graph[0][1].plot(Eb_no_sc1a, color="blue", label='Eb/No SC1A', ls='--')
range_graph[0][1].plot(Eb_no_eve, color="orange", label='Eb/No Eve', marker='x', ls=(0, (5, 10)))
range_graph[0][1].set_title("Eb/No comprarision between SC1A and Eve")
range_graph[0][1].set_ylabel('Eb/No [dB]')
range_graph[0][1].set_xlabel('Simulation Step')
range_graph[0][1].legend()

range_graph[1][0].plot(Xmtr_gain_sc1a, color="blue", label='Xmtr Gain SC1A', ls='--')
range_graph[1][0].plot(Xmtr_gain_eve, color="orange", label='Xmtr Gain Eve', marker='x', ls=(0, (5, 10)))
range_graph[1][0].set_title("Xmtr Gain comprarision between SC1A and Eve")
range_graph[1][0].set_ylabel('Xmtr Gain [dB]')
range_graph[1][0].set_xlabel('Simulation Step')
range_graph[1][0].legend()

range_graph[1][1].plot(Xmtr_gain_sc1a, color="blue", label='Xmtr Gain SC1A', ls='--')
range_graph[1][1].plot(Xmtr_gain_eve, color="orange", label='Xmtr Gain Eve', marker='x', ls=(0, (5, 10)))
range_graph[1][1].set_title("Xmtr Gain comprarision between SC1A and Eve")
range_graph[1][1].set_ylabel('Xmtr Gain [dB]')
range_graph[1][1].set_xlabel('Simulation Step')
range_graph[1][1].legend()

range_graph[2][0].plot(range_sc1a, color="blue", label='Range SC1A', ls='--')
range_graph[2][0].plot(range_eve, color="orange", label='Range Eve', ls=(0, (5, 10)))
range_graph[2][0].set_title("Range comprarision between SC1A and Eve")
range_graph[2][0].set_ylabel('Range [Km]')
range_graph[2][0].set_xlabel('Simulation Step')
range_graph[2][0].legend()

range_graph[2][1].plot(elevation_eve, color="orange", label='Range Eve', ls=(0, (5, 10)))
range_graph[2][1].set_title("Eve elevation")
range_graph[2][1].set_ylabel('Elevation')
range_graph[2][1].set_xlabel('Simulation Step')
range_graph[2][1].legend()

plt.tight_layout()
plt.show()