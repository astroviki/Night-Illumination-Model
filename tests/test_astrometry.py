import pytest
import numpy as np
from illumination_model.astrometry import AstrometryEngine, ObserverLocation

# --- Fixtures (Příprava dat) ---
@pytest.fixture(scope="module")
def engine():
    """Inicializuje astrometrický engine (načte efemeridy pouze jednou)."""
    return AstrometryEngine()

@pytest.fixture
def prague_observer():
    """Vrátí pozorovatele v Praze."""
    return ObserverLocation(latitude=50.0755, longitude=14.4378, elevation_m=200)

# --- Unit Testy ---
def test_sun_culmination(engine, prague_observer):
    """
    Ověří, že během letního slunovratu v poledne je Slunce vysoko a na jihu.
    """
    # 21. června 2025, cca 11:00 UTC (13:00 SELČ - letní čas)
    t = engine.get_time_from_utc(2025, 6, 21, 11, 0, 0)
    
    alt, az, dist = engine.calculate_sun_position(prague_observer, t)
    
    # Assertions (Ověření předpokladů)
    assert alt > 60.0, f"Elevace Slunce ({alt}°) je příliš nízká pro letní slunovrat."
    # Azimut by měl být blízko 180 (Jih)
    assert 170.0 < az < 190.0, f"Azimut Slunce ({az}°) neodpovídá poledni (očekáváno cca 180°)."
    # Vzdálenost Země-Slunce cca 1.01 AU (afélium je v červenci)
    assert 1.00 < dist < 1.02, f"Vzdálenost ({dist} AU) je mimo očekávaný rozsah."

def test_moon_distance(engine, prague_observer):
    """
    Ověří, že vzdálenost Měsíce je v fyzikálně smysluplném rozsahu.
    """
    t = engine.get_current_time()
    _, _, dist_km = engine.calculate_moon_position(prague_observer, t)
    
    # Měsíc je vzdálen 360 000 km až 405 000 km
    assert 350_000 < dist_km < 410_000, f"Vzdálenost Měsíce {dist_km} km je nesmyslná."
