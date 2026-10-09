from DOA.config.lib_config import numpy as np

class matprop_enhanced_PCM:
    def __init__(self, Tmelt, alpha, k_pcm_liq, k_pcm_sol, k_int, cp_pcm_liq, cp_pcm_sol, cp_int, rho_pcm_liq, rho_pcm_sol, rho_int, L, r, T_min, T_max):
        self.Tmelt = Tmelt # [K]
        self.alpha = alpha
        
        self.k_pcm_liq = k_pcm_liq # [kW/(m*K)]
        self.k_pcm_sol = k_pcm_sol # [kW/(m*K)]
        self.k_int = k_int # [kW/(m*K)]
        
        self.cp_pcm_liq = cp_pcm_liq # [kJ/(kg*K)]
        self.cp_pcm_sol = cp_pcm_sol # [kJ/(kg*K)]
        self.cp_int = cp_int # [kJ/(kg*K)]
        
        self.rho_pcm_liq = rho_pcm_liq # [kg/m^3]
        self.rho_pcm_sol = rho_pcm_sol # [kg/m^3]
        self.rho_int = rho_int # [kg/m^3]
        
        self.L = L # [kJ/kg]
        
        self.r = r # [ratio of volume of enhancement material]
        
        self.h_min = self.get_h(T_min, self.get_rho_pcm(T_min)) # enthalpy at SOC = 0 [kJ/m^3]
        self.h_max = self.get_h(T_max, self.get_rho_pcm(T_max)) # enthalpy at SOC = 1 [kJ/m^3]
        
    def f(self, T):
        # Compute Exponent for Sigmoid Function
        a = self.alpha*(T - self.Tmelt)
        
        # Melt fraction
        mf = 1 / (1 + np.exp(-a))
        
        # pcm thermal conductivity
        k_pcm = mf*self.k_pcm_liq + (1-mf)*self.k_pcm_sol
        
        # pcm specific heat
        cp_pcm = self.cp_pcm_sol + ((self.cp_pcm_liq-self.cp_pcm_sol)*mf) + (self.alpha*self.L) / (2 + np.exp(-a) + np.exp(a))
        
        # pcm density
        rho_pcm = mf*self.rho_pcm_liq + (1-mf)*self.rho_pcm_sol
        
        # volumetric rule of mixture for density
        rho_c = (1-self.r)*rho_pcm + self.r*self.rho_int
        
        # volumetric rule of mixture for specific heat [kJ/(m^3*K)]
        cp_c = (1-self.r)*cp_pcm*rho_pcm + self.r*self.cp_int*self.rho_int
        
        # aniostropic resistance model for thermal conductivity
        k_cv = (1-self.r)*k_pcm + self.r*self.k_int
        k_ch = (k_pcm*self.k_int) / (self.r*k_pcm + (1-self.r)*self.k_int)
        
        # Compute Specific Enthalpy of the composite with volumetric rule of mixture (ROM) [kJ/m^3]
        h_c = self.get_h(T, rho_pcm)
        
        # Compute per-CV SOC
        SOC = ((h_c - self.h_max) / (self.h_min - self.h_max))
        
        return k_cv, k_ch, cp_c, rho_c, h_c, mf, SOC
    
    def get_h(self, T, rho_pcm):
        h_pcm = self.cp_pcm_sol*(T-self.Tmelt) + ((self.cp_pcm_liq - self.cp_pcm_sol)/self.alpha)*np.log1p((np.exp(self.alpha*(T-self.Tmelt)))/2) + (self.L/2)*np.tanh((self.alpha/2)*(T-self.Tmelt))
        h_int = self.cp_int*(T-self.Tmelt)
        h_c = (1-self.r)*h_pcm*rho_pcm + self.r*h_int*self.rho_int
        
        return h_c
    
    def get_rho_pcm(self, T):
        # Compute Exponent for Sigmoid Function
        a = self.alpha*(T - self.Tmelt)
        
        # Melt fraction
        mf = 1 / (1 + np.exp(-a))
        
        # pcm density
        rho_pcm = mf*self.rho_pcm_liq + (1-mf)*self.rho_pcm_sol
        
        return rho_pcm