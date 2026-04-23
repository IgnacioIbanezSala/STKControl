import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Channel
import Secrecy_Rates as sr


df_eve = pd.read_excel("Reports/Eve_acces_transmitterCBAmanual_antena_pointing.xlsx")
df_sc1a = pd.read_excel("Reports/SAOCOM1A_acces_transmitterCBAmanual_antena_pointing.xlsx")

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
ax.hist(abs_h_t_bob, density=True,  bins='auto', histtype='stepfilled', alpha=0.2, label='H_t Bob histogram')
ax.hist(abs_h_t_eve, density=True,  bins='auto', histtype='stepfilled', alpha=0.2, label='H_t Eve histogram')
ax.set_title('H_t pdf vs histograms')
ax.legend()
plt.show()

df_eve.plot(y='Range', title='Eve range')
df_sc1a.plot(y='Range', title='Bob range')
plt.show()


#Distances of satellites to Alice
d_eve = df_eve["Range"][0:num_samples]
d_bob = df_sc1a["Range"][0:num_samples]

#Satellites C/No
cn_eve = df_eve["C/No"]
cn_bob = df_sc1a["C/No"]

#SNR
SNR_B = bob_channel.gen_SNR_STKvalues(cn_bob, h_t_bob)

SNR_E = eve_channel.gen_SNR_STKvalues(cn_eve, h_t_eve)

SNR_t = np.linspace(0, num_samples, num_samples)

snr_axes = plt.subplots(1,1)[1]
snr_axes.plot(SNR_t, 10*np.log10(SNR_B), lw=2, marker='.', color="green", label='Bob SNR [dB]')
snr_axes.plot(SNR_t, 10*np.log10(SNR_E), lw=2, marker='.', color="blue", label='EVE SNR [dB]')
snr_axes.set_xlabel('Time (seconds)')
snr_axes.set_ylabel("SNR (dB)")
snr_axes.set_title("Bob & Eve SNR's in a single acces")
plt.legend()
plt.savefig("SNRvs.png")
plt.show()

f0, axes0 = plt.subplots(1,1)
axes0.hist(10*np.log10(SNR_B), density=True,  bins='auto', histtype='stepfilled', alpha=0.2)
axes0.hist(10*np.log10(SNR_E), density=True,  bins='auto', histtype='stepfilled', alpha=0.2)
plt.show()


#Target reliability for the bob
eb = 10e-3
#Secrecy constraint (or information leakage to the eve)
delta = 10e-3
#Channel blocklenght
n = 500

def rs(df_bob, df_eve, h_t_bob, h_t_eve, n):
    Rs = []
    span = min(len(df_eve["Range"]), len(df_sc1a["Range"]))
    for i in range(span):
    
        idx_eve = df_bob.index[df_bob["Time"] == df_eve.at[i, "Time"]]
        if idx_eve.empty:
            #Rs.append(0)
            pass
        else:
            snr_b = bob_channel.gen_SNR_STKvalues(df_bob.loc[idx_eve]["C/No"], h_t_bob[i])
            snr_e = eve_channel.gen_SNR_STKvalues(df_eve.loc[i]["C/No"], h_t_eve[i])
            Rs_inst = sr.achievable_secrecy_rate(snr_b, snr_e, eb, delta, n)[1]
            Rs.append(Rs_inst)

    return Rs

Rs_sc1a = rs(df_sc1a, df_eve, h_t_bob, h_t_eve, n)

rs_axes = plt.subplots(1,1, figsize = (10,10))[1]
rs_axes.plot(Rs_sc1a, lw=2, marker='.', color="blue", label='Rs SAOCOM1A')
rs_axes.set_xlabel('Time (seconds)')
rs_axes.set_ylabel('Secrecy Rate')
rs_axes.set_title('Bob Secrecy Rate in a single access')
plt.legend()
plt.savefig('SecrecyRate.png')
plt.show()