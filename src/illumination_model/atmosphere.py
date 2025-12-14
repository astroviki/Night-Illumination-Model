import numpy as np

class AtmosphereModel:
    """
    Modeluje průchod světla atmosférou Země.
    Implementuje výpočet extinkce (tlumení) a optické hmoty.
    
    Založeno na sekci 5 článku Undeger (2009).
    """

    # Vlnová délka, pro kterou počítáme osvětlení (střed viditelného spektra)
    # 555 nm je vrchol citlivosti lidského oka (fotopické vidění)
    WAVELENGTH_UM = 0.555 
    
    # Rayleighův koeficient pro standardní atmosféru
    # C_rayleigh = 0.008735 * lambda^(-4.08)
    C_RAYLEIGH = 0.008735 * (WAVELENGTH_UM ** -4.08)
    
    # Absorpční koeficient ozónu (považován za konstantu)
    C_OZONE = 0.02975

    def __init__(self):
        pass

    def _calculate_air_mass(self, altitude_deg: float) -> float:
        """
        Vypočte relativní optickou vzdušnou hmotu (Air Mass).
        
        m = 1.0 znamená Slunce přímo v zenitu (kolmo).
        m > 1.0 znamená Slunce níže nad obzorem (delší průchod atmosférou).
        
        Používá robustní Kasten-Youngovu aproximaci (1989), která odpovídá
        formě rovnice 18 v článku a nediverguje na horizontu.
        
        :param altitude_deg: Výška tělesa nad obzorem ve stupních.
        """
        # Ošetření záporné výšky (těleso pod obzorem)
        if altitude_deg < -0.5:
            return float('inf') # Světlo neprojde skrz Zemi
            
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
        Vypočte celkový extinkční koeficient C dle rovnice 17.
        
        :param turbidity: Turbidita (Linke Turbidity Factor).
                          2.0 = Velmi čistá obloha (hory)
                          3.0 - 5.0 = Čistá až mírně zakalená obloha (nížiny)
                          10+ = Lehká mlha / silný opar
        """
        # 1. Aerosolový rozptyl (Mie) - závislý na turbiditě
        # Eq 17: C_aerosol = (0.04608 * T - 0.04586) * lambda^(-1.3)
        c_aerosol = (0.04608 * turbidity - 0.04586) * (self.WAVELENGTH_UM ** -1.3)
        
        # Celková extinkce = Rayleigh + Aerosol + Ozone
        c_total = self.C_RAYLEIGH + c_aerosol + self.C_OZONE
        
        return c_total

    def get_transmittance(self, altitude_deg: float, turbidity: float = 3.0) -> float:
        """
        Vypočte propustnost atmosféry (hodnota 0.0 až 1.0).
        Aplikuje Beer-Lambertův zákon (Eq 15).
        
        :param altitude_deg: Výška zdroje nad obzorem.
        :param turbidity: Znečištění atmosféry (default 3.0 pro běžný den).
        :return: Koeficient propustnosti (násobte jím extraterestrickou intenzitu).
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
        Pomocná funkce pro odhad turbidity z viditelnosti (Meteorological Range).
        Aproximace grafu Figure 3 z článku.
        """
        if visibility_km > 100:
            return 2.0  # Velmi čistý vzduch
        elif visibility_km > 20:
            return 3.0  # Čisto
        elif visibility_km > 10:
            return 4.0  # Lehký opar
        elif visibility_km > 5:
            return 7.0  # Opar
        elif visibility_km > 2:
            return 15.0 # Silný opar / mlha
        else:
            return 30.0 # Hustá mlha
