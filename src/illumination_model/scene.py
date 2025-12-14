import numpy as np
from skyfield.timelib import Time
from .astrometry import AstrometryEngine, ObserverLocation
from .sources.sun import SunModel
from .sources.moon import MoonModel
from .atmosphere import AtmosphereModel

class IlluminationScene:
    """
    Hlavní třída pro simulaci venkovního osvětlení.
    Sjednocuje výpočty polohy, zdrojů světla a atmosféry.
    """

    # Osvětlení od hvězd NAD ATMOSFÉROU (Extraterrestrial)
    # Odvozeno v článku (Eq 14): 0.00022 / 0.810584 = 0.0002714 lux
    STAR_ILLUMINANCE_EXO_LUX = 0.0002714

    def __init__(self):
        # Inicializace pod-systémů
        self.engine = AstrometryEngine()
        self.sun_model = SunModel()
        self.moon_model = MoonModel(self.engine)
        self.atmos_model = AtmosphereModel()

    def calculate_illumination(self, 
                             latitude: float, 
                             longitude: float, 
                             elevation_m: float, 
                             time: Time, 
                             turbidity: float = 3.0) -> dict:
        """
        Vypočte celkové osvětlení scény pro dané místo a čas.
        """
        observer = ObserverLocation(latitude, longitude, elevation_m)

        # 1. SLUNCE
        sun_alt, sun_az, _ = self.engine.calculate_sun_position(observer, time)
        sun_exo = self.sun_model.get_extraterrestrial_illuminance(time)
        sun_trans = self.atmos_model.get_transmittance(sun_alt, turbidity)
        
        # Projekce na vodorovnou plochu: max(0, sin(alt))
        sun_factor = max(0.0, np.sin(np.radians(sun_alt)))
        sun_surface = sun_exo * sun_trans * sun_factor

        # 2. MĚSÍC
        moon_alt, moon_az, moon_dist = self.engine.calculate_moon_position(observer, time)
        moon_exo = self.moon_model.get_extraterrestrial_illuminance(time)
        moon_trans = self.atmos_model.get_transmittance(moon_alt, turbidity)
        
        moon_factor = max(0.0, np.sin(np.radians(moon_alt)))
        moon_surface = moon_exo * moon_trans * moon_factor

        # 3. HVĚZDY (OPRAVENO)
        # Hvězdy nyní procházejí atmosférou.
        # Protože jsou rozprostřeny po celé obloze, použijeme pro útlum
        # referenční propustnost v Zenitu (90 stupňů).
        # Při vysoké turbiditě (mlha) bude 'stars_trans' velmi malé číslo.
        stars_trans = self.atmos_model.get_transmittance(90.0, turbidity)
        stars_surface = self.STAR_ILLUMINANCE_EXO_LUX * stars_trans

        # 4. CELKEM
        total_lux = sun_surface + moon_surface + stars_surface

        return {
            "total_lux": total_lux,
            "sun_lux": sun_surface,
            "moon_lux": moon_surface,
            "stars_lux": stars_surface,
            "sun_altitude": sun_alt,
            "moon_altitude": moon_alt,
            "moon_phase_angle": np.degrees(self.moon_model.calculate_phase_angle(time))
        }
