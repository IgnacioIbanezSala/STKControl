import numpy as np
import scipy as sp
from scipy import stats
from math import log2, log, sqrt
import matplotlib.pyplot as plt
import pandas as pd
import Channel
import Secrecy_Rates as sr


df_eve = pd.read_excel("Reports/Eve_transmitterCBA.xlsx")
df_sc1a = pd.read_excel("Reports/SAOCOM1A_transmitterCBA.xlsx")

print("eve report lenght:", len(df_eve["Range"]))
print("bob report lenght:", len(df_sc1a["Range"]))

t_0 = 0
t_f = 10
num_samples = min(len(df_eve["Range"]), len(df_sc1a["Range"]))
b_b = 0.005
m_b = 26
omega_b = 0.515
beta_b = 0.5
b_e = 0.005
m_e = 26
omega_e = 0.515
beta_e = 0.5

fig, ax = plt.subplots(1, 1)
eve_channel = Channel.Short_Packed_Channel(b_e, m_e, omega_e, beta_e, num_samples)
bob_channel = Channel.Short_Packed_Channel(b_b, m_b, omega_b, beta_b, num_samples)

h_t_bob, abs_h_t_bob = bob_channel.shadowed_rician(t_0, t_f)
h_t_eve, abs_h_t_eve = eve_channel.shadowed_rician(t_0, t_f)


ch_envelope_pdf = bob_channel.channel_envelope_pdf(t_0, t_f)
t = np.linspace(t_0, t_f, num_samples)
ax.plot(t, ch_envelope_pdf, 'k-', lw=2, label='frozen pdf')
ax.hist(abs_h_t_bob, density=True,  bins='auto', histtype='stepfilled', alpha=0.2)
ax.hist(abs_h_t_eve, density=True,  bins='auto', histtype='stepfilled', alpha=0.2)
#plt.show()

df_eve.plot(y='Range')
df_sc1a.plot(y='Range')
#plt.show()

# Antenna gain
phi = 1.35 #get from STK
phi_rx = 1.6 #LEO antenna pattern
Ga = np.power(2, ((-phi**2)/(phi_rx**2)))
Gb = 1
Ge = 1

#Transmit power of Alice
Pa = 1

#Distances of satellites to Alice, to be got from STK
d_eve = df_eve["Range"][0:num_samples]
d_bob = df_sc1a["Range"][0:num_samples]

idx_eve = df_sc1a.index[df_sc1a["Time"] == df_eve.at[14, "Time"]]
print(df_sc1a.loc[idx_eve, "Range"].values[0])
#wavelength
wl = 120

#Free space path loss
L_eve = wl / (4*np.pi*d_eve)
L_bob = wl / (4*np.pi*d_bob)

#Desired SNR means for Bob and Eve
snr_mean_bob = np.power(10,5/10) #5dB
snr_mean_eve = np.power(10,-3/10) #-3dB

#Noise
noise = np.random.normal(0,1,num_samples)

#SNR

SNR_B = np.array([], dtype=float)
SNR_E = np.array([], dtype=float)

SNR_B = bob_channel.gen_SNR(Pa, Ga, Gb, L_bob, h_t_bob)
#bob_scale = snr_mean_bob/np.mean(SNR_B)
bob_scale = 1
SNR_B = bob_scale * SNR_B


SNR_E = eve_channel.gen_SNR(Pa, Ga, Ge, L_eve, h_t_eve)
#eve_scale = snr_mean_eve/np.mean(SNR_E)
eve_scale = 1
SNR_E = eve_scale * SNR_E

SNR_t = np.linspace(0, num_samples, num_samples)

snr_axes = plt.subplots(1,1)[1]
snr_axes.plot(SNR_t, 10*np.log10(SNR_B), lw=2, marker='.', color="green", label='Bob SNR [dB]')

snr_axes.plot(SNR_t, 10*np.log10(SNR_E), lw=2, marker='.', color="blue", label='EVE SNR [dB]')
plt.legend()
#plt.show()

f0, axes0 = plt.subplots(1,1)
#axes0.plot(SNR_t, SNR_B_2)
axes0.hist(10*np.log10(SNR_B), density=True,  bins='auto', histtype='stepfilled', alpha=0.2)

axes0.hist(10*np.log10(SNR_E), density=True,  bins='auto', histtype='stepfilled', alpha=0.2)
#plt.show()


#Target reliability for the bob
eb = 10e-3
#Secrecy constraint (or information leakage to the eve)
delta = 10e-3
#Channel blocklenght
n = 500

Rs = []
times = []
#idx_eve = []
for i in range(num_samples):
    
    idx_eve = df_sc1a.index[df_sc1a["Time"] == df_eve.at[i, "Time"]]
    if idx_eve.empty:
        #Rs.append(0)
        pass
    else:
        l_bob = wl / (4*np.pi*df_sc1a.loc[idx_eve]["Range"])
        l_eve = wl / (4*np.pi*df_eve.loc[idx_eve]["Range"])
        snr_b = bob_channel.gen_SNR_STKvalues(df_sc1a.loc[idx_eve]["C_No"], h_t_bob[i])
        snr_e = eve_channel.gen_SNR_STKvalues(df_eve.loc[idx_eve]["C_No"], h_t_eve[i])
        Rs_inst = sr.achievable_secrecy_rate(snr_b, snr_e, eb, delta, n)[1]
        Rs.append(Rs_inst)
        times.append(df_eve.loc[i]["Time"])

rs_axes = plt.subplots(1,1, figsize = (10,10))[1]
rs_axes.plot(times, Rs, lw=2, marker='.', color="blue", label='Rs')
rs_axes.tick_params(axis='x', labelrotation=70, labelsize = 4)
plt.legend()
plt.show()