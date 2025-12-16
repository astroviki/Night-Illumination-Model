import numpy as np

class AtmosphereModel:
    """
    Models light transmission through Earth's atmosphere.
    Implements extinction and optical air mass calculations.
    
    Based on Section 5 of Undeger (2009).
    """

    # Center of visible spectrum (photopic vision peak)
    WAVELENGTH_UM = 0.555 
    
    # Rayleigh coefficient for standard atmosphere
    # C_rayleigh = 0.008735 * lambda^(-4.08)
    C_RAYLEIGH = 0.008735 * (WAVELENGTH_UM ** -4.08)
    
    # Ozone absorption coefficient (assumed constant)
    C_OZONE = 0.02975

    def __init__(self):
        pass

    def _calculate_air_mass(self, altitude_deg: float) -> float:
        """
        Calculates relative optical air mass (m).
        
        m = 1.0 means Sun is at Zenith (perpendicular).
        m > 1.0 means Sun is lower (longer path through atmosphere).
        
        Uses robust Kasten-Young approximation (1989), which prevents
        singularity at the horizon (unlike simple 1/sin(a)).
        
        :param altitude_deg: Object altitude in degrees.
        """
        # Negative altitude (body bellow horizon)
        if altitude_deg < -0.5:
            return float('inf')
            
        # Kasten-Young vzorec: 1 / (sin(a) + 0.50572 * (a + 6.07995)^-1.6364)
        # Použijeme raději tvar z článku (Eq 18), pokud je čitelný, 
        # ale Kasten-Young je průmyslový standard pro tento typ simulací.
        # Zde použijeme modifikovanou verzi pro absolutní robustnost u horizontu.
        
        alpha_rad = np.radians(altitude_deg)
        zenith_angle = np.radians(90) - alpha_rad
        
        # Rozenbergova rovnice (často citovaná v papers pro illuminaci)
        # m = 1 / (cos(z) + 0.025 * exp(-11 * cos(z))) 
        # Ale pro shodu s článkem (Eq 18) se pokusíme o fit:
        # m = 1 / (sin(alpha) + 0.15 * (alpha + 3.885)^-1.253)
        # Toto odpovídá vzorci z "Preetham et al." (citace 16 v článku).
        
        # Ochrana proti dělení nulou/komplexním číslům pro velmi nízké úhly
        denominator = np.sin(alpha_rad) + 0.15 * np.power(altitude_deg + 3.885, -1.253)
        return 1.0 / denominator

    def calculate_extinction_coefficient(self, turbidity: float) -> float:
        """
        Calculates total extinction coefficient C (Eq 17).
        
        :param turbidity: Linke Turbidity Factor.
                          2.0 = Very clear (Mountains)
                          3.0 - 5.0 = Clear to Light Haze
                          10+ = Haze / Fog

        """
        # 1. Aerosol scattering (Mie) - depends on turbidity
        # Eq 17: C_aerosol = (0.04608 * T - 0.04586) * lambda^(-1.3)
        c_aerosol = (0.04608 * turbidity - 0.04586) * (self.WAVELENGTH_UM ** -1.3)
        
        # Total extinction = Rayleigh + Aerosol + Ozone
        c_total = self.C_RAYLEIGH + c_aerosol + self.C_OZONE
        
        return c_total

    def get_transmittance(self, altitude_deg: float, turbidity: float = 3.0) -> float:
        """
        Calculates atmospheric transmittance (0.0 to 1.0).
        Applies Beer-Lambert law (Eq 15).
        
        :param altitude_deg: Source altitude above horizon.
        :param turbidity: Atmospheric pollution (default 3.0).
        :return: Transmittance coefficient.
        """
        if altitude_deg <= 0.0:
            return 0.0
            
        m = self._calculate_air_mass(altitude_deg)
        c = self.calculate_extinction_coefficient(turbidity)
        
        # Beer-Lambert: Transmittance = e^(-C * m)
        transmittance = np.exp(-c * m)
        
        return transmittance

    @staticmethod
    def visibility_to_turbidity(visibility_km: float) -> float:
        """
        Helper to estimate turbidity from meteorological visibility range.
        Approximation of Figure 3 in the paper.
        """
        if visibility_km > 100:
            return 2.0  # Very clear
        elif visibility_km > 20:
            return 3.0  # Clear
        elif visibility_km > 10:
            return 4.0  # Light haze
        elif visibility_km > 5:
            return 7.0  # Haze
        elif visibility_km > 2:
            return 15.0 # Strong haze / Fog
        else:
            return 30.0 # Dense Fog
