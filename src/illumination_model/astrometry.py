import os
from skyfield.api import load, wgs84, Loader
from skyfield.timelib import Time
import numpy as np

# Cesta pro stahování astronomických dat (ephemeridy)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data')
load = Loader(DATA_DIR)

class ObserverLocation:
    """
    Reprezentuje pozorovatele na povrchu Země.
    """
    def __init__(self, latitude: float, longitude: float, elevation_m: float = 0.0):
        """
        :param latitude: Zeměpisná šířka (stupně, +N)
        :param longitude: Zeměpisná délka (stupně, +E)
        :param elevation_m: Nadmořská výška v metrech
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation_m
        # Vytvoření objektu pozorovatele v systému WGS84
        self.geo_loc = wgs84.latlon(latitude, longitude, elevation_m)

class AstrometryEngine:
    """
    Zajišťuje výpočty polohy nebeských těles (Slunce, Měsíc) pro daný čas a místo.
    Nahrazuje aproximační Algoritmy 1, 2 a 3 z původního článku robustním řešením.
    """
    def __init__(self):
        # Načtení efemerid DE421 (zahrnuje planety, Slunce, Měsíc)
        # Pokud soubor neexistuje, Skyfield ho stáhne.
        print("Načítám efemeridy DE421...")
        self.planets = load('de421.bsp')
        self.earth = self.planets['earth']
        self.sun = self.planets['sun']
        self.moon = self.planets['moon']
        self.ts = load.timescale()

    def get_current_time(self):
        """Vrátí aktuální čas Skyfield."""
        return self.ts.now()

    def get_time_from_utc(self, year, month, day, hour, minute, second):
        """Vytvoří časový objekt z UTC data."""
        return self.ts.utc(year, month, day, hour, minute, second)

    def calculate_sun_position(self, observer: ObserverLocation, time: Time):
        """
        Vypočte polohu Slunce v lokálních souřadnicích (Azimut, Elevace).
        
        Odpovídá sekci 3.2 článku[cite: 53], ale s vyšší přesností.
        
        :return: (altitude_degrees, azimuth_degrees, distance_au)
        """
        observer_topos = self.earth + observer.geo_loc
        astrometric = observer_topos.at(time).observe(self.sun)
        apparent = astrometric.apparent()
        
        alt, az, distance = apparent.altaz()
        return alt.degrees, az.degrees, distance.au

    def calculate_moon_position(self, observer: ObserverLocation, time: Time):
        """
        Vypočte polohu Měsíce v lokálních souřadnicích.
        
        Odpovídá sekci 3.3 článku[cite: 82].
        
        :return: (altitude_degrees, azimuth_degrees, distance_km)
        """
        observer_topos = self.earth + observer.geo_loc
        astrometric = observer_topos.at(time).observe(self.moon)
        apparent = astrometric.apparent()
        
        alt, az, distance = apparent.altaz()
        return alt.degrees, az.degrees, distance.km

    def get_sun_earth_distance_au(self, time: Time):
        """Vrátí vzdálenost Země-Slunce v AU pro daný čas."""
        earth_pos = self.earth.at(time).position.au
        sun_pos = self.sun.at(time).position.au
        return np.linalg.norm(np.array(earth_pos) - np.array(sun_pos))
