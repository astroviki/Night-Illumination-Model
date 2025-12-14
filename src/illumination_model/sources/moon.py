import numpy as np
from skyfield.api import position_of_radec, load
from skyfield.timelib import Time
from ..astrometry import AstrometryEngine, ObserverLocation

class MoonModel:
    """
    Fyzikální model Měsíce zahrnující fázi, popelavý svit (Earthshine)
    a opoziční efekt (Opposition Surge).
    
    Implementace vychází z článku Undeger (2009), sekce 4.2.
    """
    
    # Poloměr Měsíce v km
    MOON_RADIUS_KM = 1737.4
    
    # Solární konstanta v Luxech (převzato z článku, sekce 4.1)
    SOLAR_ILLUMINANCE_LUX = 127500.0
    
    # Solární iradiance ve W/m2 (použito pro škálování Earthshine)
    # Sekce 4.2 uvádí E_sm = 1300 W/m2
    SOLAR_IRRADIANCE_WM2 = 1300.0
    
    # Průměrné vizuální albedo Měsíce
    MOON_ALBEDO = 0.12
    
    # Geometrický faktor pro Lambertovu kouli
    LAMBERT_SPHERE_FACTOR = 2.0 / 3.0

    def __init__(self, astrometry_engine: AstrometryEngine):
        self.engine = astrometry_engine

    def calculate_phase_angle(self, time: Time) -> float:
        """
        Vypočte fázový úhel Měsíce (úhel Slunce-Měsíc-Země).
        0 rad = Úplněk, PI rad = Nov.
        """
        sun_pos = self.engine.sun.at(time).position.km
        moon_pos = self.engine.moon.at(time).position.km
        earth_pos = self.engine.earth.at(time).position.km
        
        v_me = earth_pos - moon_pos
        v_ms = sun_pos - moon_pos
        
        v_me_u = v_me / np.linalg.norm(v_me)
        v_ms_u = v_ms / np.linalg.norm(v_ms)
        
        dot_product = np.dot(v_me_u, v_ms_u)
        dot_product = np.clip(dot_product, -1.0, 1.0)
        
        return np.arccos(dot_product)

    def _calculate_opposition_surge(self, phase_angle_rad: float) -> float:
        """
        Vypočte koeficient nárůstu jasu při opozici (úplňku).
        """
        phi_deg = np.degrees(phase_angle_rad)
        if phi_deg <= 7.0:
            val = 1.27 - 0.045 * (abs(phi_deg) - 1)
            return max(val, 1.0)
        return 1.0

    def _calculate_earthshine_wm2(self, moon_phase_angle: float) -> float:
        """
        Vypočte intenzitu popelavého svitu Země dopadajícího na Měsíc ve W/m^2.
        Implementace rovnice 11.
        """
        earth_phase_p = np.pi - moon_phase_angle
        epsilon = 1e-4
        
        if earth_phase_p < epsilon or earth_phase_p > (np.pi - epsilon):
             return 0.0

        term1 = np.sin(earth_phase_p / 2)
        term2 = np.tan(earth_phase_p / 2)
        term3 = np.log(1.0 / np.tan(earth_phase_p / 4))
        
        # Výsledek je ve W/m2 (konstanta 0.095 vychází z článku)
        e_eas = 0.095 * (1 - term1 * term2 * term3)
        return max(0.0, e_eas)

    def get_extraterrestrial_illuminance(self, time: Time) -> float:
        """
        Vypočte celkovou osvětlenost od Měsíce těsně nad atmosférou Země (E_MT).
        """
        phi = self.calculate_phase_angle(time)
        dist_km = self.engine.earth.at(time).observe(self.engine.moon).distance().km
        
        # Opoziční efekt
        o_eff = self._calculate_opposition_surge(phi)
        
        # Fázová funkce pro přímé Slunce
        epsilon = 1e-4
        if phi < epsilon:
            phase_factor = 1.0
        elif phi > (np.pi - epsilon):
            phase_factor = 0.0
        else:
            term1 = np.sin(phi / 2)
            term2 = np.tan(phi / 2)
            term3 = np.log(1.0 / np.tan(phi / 4))
            phase_factor = 1 - term1 * term2 * term3
        
        # 1. Přímé sluneční světlo (Lux)
        e_reflected_sun = self.SOLAR_ILLUMINANCE_LUX * phase_factor
        
        # 2. Earthshine (W/m2 -> Lux)
        # Nejdříve získáme hodnotu ve W/m2
        e_earthshine_wm2 = self._calculate_earthshine_wm2(phi)
        # Převod na Luxy pomocí poměru solárních konstant
        # (127500 lx / 1300 W/m2) cca 98 lx/(W/m2)
        conversion_ratio = self.SOLAR_ILLUMINANCE_LUX / self.SOLAR_IRRADIANCE_WM2
        e_earthshine_lux = e_earthshine_wm2 * conversion_ratio

        # Finální složení
        geometry_factor = (self.MOON_RADIUS_KM / dist_km)**2
        
        total_illuminance = (
            self.LAMBERT_SPHERE_FACTOR * self.MOON_ALBEDO * o_eff * geometry_factor * (e_reflected_sun + e_earthshine_lux)
        )
        
        return total_illuminance
