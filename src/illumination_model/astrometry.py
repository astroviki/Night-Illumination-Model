import os
from skyfield.api import load, wgs84, Loader
from skyfield.timelib import Time
import numpy as np

# Path for downloading astronomical data (ephemeris)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data')
load = Loader(DATA_DIR)

class ObserverLocation:
    """
    Represents an observer on the Earth's surface
    """
    def __init__(self, latitude: float, longitude: float, elevation_m: float = 0.0):
        """
        :param latitude: Geographic latitude (degrees, +N)
        :param longitude: Geographic longitude (degrees, +E)
        :param elevation_m:  Elevation above sea level  in meters
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation_m
        # Create observer object in WGS84 system
        self.geo_loc = wgs84.latlon(latitude, longitude, elevation_m)

class AstrometryEngine:
    """
    Handles calculation of celestial body positions (Sun, Moon) for a given time and location.
    Replaces approximation Algorithms 1, 2, and 3 from the original paper with a robust solution.
    """
    def __init__(self):
        # Load DE421 ephemeris (includes planets, Sun, Moon)
        # If the file does not exist, Skyfield will download it.
        print("Loading DE421 ephemeris...")
        self.planets = load('de421.bsp')
        self.earth = self.planets['earth']
        self.sun = self.planets['sun']
        self.moon = self.planets['moon']
        self.ts = load.timescale()

    def get_current_time(self):
        """Returns current Skyfield time."""
        return self.ts.now()

    def get_time_from_utc(self, year, month, day, hour, minute, second):
        """Creates a time object from UTC date components."""
        return self.ts.utc(year, month, day, hour, minute, second)

    def calculate_sun_position(self, observer: ObserverLocation, time: Time):
        """
        Calculates Sun's position in local coordinates (Azimuth, Elevation).
        
        Corresponds to Section 3.2 of the paper but with higher precision.
        
        :return: (altitude_degrees, azimuth_degrees, distance_au)
        """
        observer_topos = self.earth + observer.geo_loc
        astrometric = observer_topos.at(time).observe(self.sun)
        apparent = astrometric.apparent()
        
        alt, az, distance = apparent.altaz()
        return alt.degrees, az.degrees, distance.au

    def calculate_moon_position(self, observer: ObserverLocation, time: Time):
        """
        Calculates Moon's position in local coordinates.
        
        Corresponds to Section 3.3 of the paper.
        
        :return: (altitude_degrees, azimuth_degrees, distance_km)
        """
        observer_topos = self.earth + observer.geo_loc
        astrometric = observer_topos.at(time).observe(self.moon)
        apparent = astrometric.apparent()
        
        alt, az, distance = apparent.altaz()
        return alt.degrees, az.degrees, distance.km

    def get_sun_earth_distance_au(self, time: Time):
        """Return distance Earth-Sun for given time."""
        earth_pos = self.earth.at(time).position.au
        sun_pos = self.sun.at(time).position.au
        return np.linalg.norm(np.array(earth_pos) - np.array(sun_pos))
