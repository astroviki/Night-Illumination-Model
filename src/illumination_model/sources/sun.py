import numpy as np
from skyfield.timelib import Time

class SunModel:
    """
    Physical model of the Sun as a light source.
    Implements calculation of Extraterrestrial Illuminance.
    """
    # Solar constant in Lux (taken from Undeger 2009, Section 4.1)
    SOLAR_CONSTANT_LUX = 127500.0
    
    # Eccentricity of Earth's orbit
    ECCENTRICITY = 0.01672

    def __init__(self):
        pass

    def get_extraterrestrial_illuminance(self, time: Time) -> float:
        """
        Calculates solar illuminance just above the atmosphere (E_ST).
        Accounts for the varying Earth-Sun distance throughout the year.
        
        Based on Equation (9) in Undeger (2009).
        
        :param time: Skyfield Time object
        :return: Illuminance in lux (lx)
        """
        # Get Julian Date (tt = Terrestrial Time)
        jd = time.tt
        
        # Implementation of Equation (9)
        # E_ST = E_SC * ((1 + e * cos(2pi(JD-2)/365.2))^2) / (1-e^2)
        term = np.cos(2 * np.pi * (jd - 2) / 365.2)
        numerator = (1 + self.ECCENTRICITY * term)**2
        denominator = 1 - (self.ECCENTRICITY**2)
        
        e_st = self.SOLAR_CONSTANT_LUX * (numerator / denominator)
        
        return e_st
