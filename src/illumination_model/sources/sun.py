import numpy as np
from skyfield.timelib import Time

class SunModel:
    """
    Fyzikální model Slunce jako světelného zdroje.
    Implementuje výpočet intenzity světla nad atmosférou (Extraterrestrial Illuminance).
    """
    
    # Solární konstanta v luxech (převzato z článku, sekce 4.1)
    # Undeger uvádí E_sc = 127 500 lux
    SOLAR_CONSTANT_LUX = 127500.0
    
    # Excentricita oběžné dráhy Země
    ECCENTRICITY = 0.01672

    def __init__(self):
        pass

    def get_extraterrestrial_illuminance(self, time: Time) -> float:
        """
        Vypočte intenzitu slunečního záření těsně nad atmosférou (E_ST).
        Zohledňuje měnící se vzdálenost Země od Slunce během roku.
        
        Vychází z rovnice (9) v článku Undeger (2009).
        
        :param time: Skyfield Time objekt
        :return: Osvětlenost v luxech (lx)
        """
        # Získání Juliánského data (tt = Terrestrial Time)
        jd = time.tt
        
        # Implementace rovnice (9) 
        # E_ST = E_SC * ((1 + e * cos(2pi(JD-2)/365.2))^2) / (1-e^2)
        term = np.cos(2 * np.pi * (jd - 2) / 365.2)
        numerator = (1 + self.ECCENTRICITY * term)**2
        denominator = 1 - (self.ECCENTRICITY**2)
        
        e_st = self.SOLAR_CONSTANT_LUX * (numerator / denominator)
        
        return e_st
