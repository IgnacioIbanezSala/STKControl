import numpy as np
from scipy import stats, special
from math import sqrt


class Short_Packed_Channel():
  def __init__(self, b_i, m_i, omega_i, beta_i, num_samples):
    self.b_i = b_i
    self.m_i = m_i
    self.omega_i = omega_i
    self.beta_i = beta_i
    self.num_samples = num_samples
    pass
  
  def shadowed_rician(self, start, stop):
    t = np.linspace(start, stop, self.num_samples)
    h_t = []
    a_i = np.random.uniform(0, 2*np.pi, self.num_samples)
    r_i2 = stats.nakagami.rvs(nu=self.m_i, scale=np.sqrt(self.omega_i), size=self.num_samples)
    r_i1 = stats.rayleigh.rvs(scale=np.sqrt(self.b_i), size=self.num_samples)
    abs_h_t = []
    for t_i in range(len(t)):
        val = r_i1[t_i] * np.exp(complex(0,a_i[t_i])) + r_i2[t_i] * np.exp(complex(0, self.beta_i))
        abs_val = abs(val)
        h_t.append(val)
        abs_h_t.append(abs_val)
    return np.array(h_t), np.array(abs_h_t)

  def channel_envelope_pdf(self, start, stop):
      x = np.linspace(start, stop, self.num_samples)
      f_abs_h_t = []
      for i in range(len(x)):
          z = ((self.omega_i*(x[i]**2))/(2*self.b_i*(2*self.b_i*self.m_i+self.omega_i)))

          val_0 = np.power(((2*self.b_i*self.m_i)/((2*self.b_i*self.m_i)+self.omega_i)), self.m_i)

          val_1 = (x[i]/(self.b_i))

          val_2 = np.exp(((-(x[i])**2)/(2*(self.b_i))))

          val_3 = special.hyp1f1(self.m_i, 1, z)

          val = val_0 * val_1 * val_2 * val_3

          f_abs_h_t.append(val)
      return np.array(f_abs_h_t)
  
  def gen_SNR(self, Pa, Ga, Gi, Li, h_t):
    SNR = Pa * Ga * Gi * Li * (abs(h_t) ** 2) / (1**2)
    return SNR
  
  def gen_SNR_STKvalues(self, stk_cn, h_t):
    cn = np.power(10, stk_cn/10)
    SNR = cn * (abs(h_t) ** 2) / (1**2)
    return SNR
  




