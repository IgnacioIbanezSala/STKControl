from math import sqrt, log, log2
from scipy import special
import numpy as np

def inv_Q(x):
    return sqrt(2) * special.erfinv(1-2*x)

def achievable_secrecy_rate(SNR_a, SNR_b, eb, delta, n):
  #Secrecy capacity
  Cb = log2(1 + SNR_a)
  Ce = log2(1 + SNR_b)
  Cs = max((Cb - Ce), 0)
  #Channel dispersions
  Vb = (1/(log(2)**2)) * (SNR_a**2 + 2*SNR_a)/((1 + SNR_a)**2)
  Ve = (1/(log(2)**2)) * (SNR_b**2 + 2*SNR_b)/((1 + SNR_b)**2)
  #Instantaneous achievable secrecy rate
  Rs = Cs - sqrt(Vb/n) * inv_Q(eb) - sqrt(Ve/n) * inv_Q(delta)
  return Rs, Cs

def achievable_secrecy_rate_lower_bound(b_i, m_i, omega_i, Pa, G_a, G_i, L_i, mean_SNR_a, mean_SNR_b, scale, eb, delta, n):
  phi_b = 0.5772/4 + np.log(2)/4 + np.log(b_i)/4 + (1/4) * np.power(((2*b_i*m_i)/(2*b_i*m_i+omega_i)), m_i) * special.hyp2f1(1, m_i, 1, (omega_i)/(2*b_i*(2*b_i*m_i+omega_i)))

  val0 = (inv_Q(eb)/(np.log(2)*np.sqrt(n)))*np.sqrt(1-(1/((1+mean_SNR_a)**2)))
  val1 = (inv_Q(delta)/(np.log(2)*np.sqrt(n)))*np.sqrt(1-(1/((1+mean_SNR_b)**2)))
  Cs = np.log2(1+Pa*G_a*G_i*L_i*scale*phi_b) - np.log2(1+mean_SNR_b)
  val_0 = Cs - val0 - val1

  return val_0

def SNR_mean_square(b_i, m_i, omega_i, Pa, Gi, Ga, scale, L_i):
  aux_val = np.power(((2*b_i*m_i)/((2*b_i*m_i)+omega_i)), m_i)
  aux_val_2 = (omega_i/((2*b_i*m_i)+omega_i))
  phi_2 = special.hyp2f1(3, m_i, 1, aux_val_2)
  SNR_mean = ((Pa * Gi * Ga * L_i*scale)**2) * 8*(b_i**2) * aux_val * phi_2

  return SNR_mean

def secrecy_rate_approx(mean_SNR_i, mean_SNR_i2, scale, scale2, PA, GA, G_i, G_i2, L_i, L_i2, b_i, b_i2, m_i, m_i2, Omega_i, Omega_i2, delta, eb, n):
  E_SNR = SNR_mean_square (b_i, m_i, Omega_i, PA, G_i, GA,scale , L_i)
  E_SNR_2 = SNR_mean_square (b_i2, m_i2, Omega_i2, PA, G_i2, GA, scale2 , L_i2)

  val0 = (inv_Q(eb)/(np.log(2)*np.sqrt(n)))*np.sqrt(1-(1/((1+mean_SNR_i)**2)))

  val1 = (inv_Q(delta)/(np.log(2)*np.sqrt(n)))*np.sqrt(1-(1/((1+mean_SNR_i2)**2)))

  Ci = np.log2(1+mean_SNR_i)-(E_SNR-(mean_SNR_i**2))/(2*np.log(2)*(1+mean_SNR_i))

  Ci2 = np.log2(1+mean_SNR_i2)-(E_SNR_2-(mean_SNR_i2**2))/(2*np.log(2)*(1+mean_SNR_i2))

  Cs = Ci - Ci2

  Rs = Cs - val0 - val1
  return Rs