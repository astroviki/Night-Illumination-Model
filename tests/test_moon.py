import pytest
import numpy as np
from illumination_model.astrometry import AstrometryEngine
from illumination_model.sources.moon import MoonModel

@pytest.fixture(scope="module")
def engine():
    return AstrometryEngine()

@pytest.fixture
def moon_model(engine):
    return MoonModel(engine)

def test_full_moon_brightness(engine, moon_model):
    """
    Test superúplňku (17. října 2024).
    Očekáváme maximální jas (cca 0.2 - 0.35 lux).
    """
    # Čas blízko úplňku
    t = engine.get_time_from_utc(2024, 10, 17, 11, 26, 0)
    
    lux = moon_model.get_extraterrestrial_illuminance(t)
    phi = moon_model.calculate_phase_angle(t)
    phi_deg = np.degrees(phi)
    
    print(f"\n--- Supermoon Test ---")
    print(f"Fázový úhel: {phi_deg:.4f}°")
    print(f"Intenzita:   {lux:.4f} lx")
    
    # Úplněk by měl mít fázový úhel blízký 0
    assert phi_deg < 5.0
    # Jas by měl být vysoký (typický úplněk je 0.1-0.3 lux, superúplněk více)
    assert 0.2 < lux < 0.45
    
    # Ověření, že funguje Opposition Surge (koeficient > 1)
    surge = moon_model._calculate_opposition_surge(phi)
    assert surge > 1.0

def test_new_moon_earthshine(engine, moon_model):
    """
    Test novu (2. října 2024).
    Očekáváme velmi nízký jas, ale NE nulu (kvůli Earthshine).
    """
    t = engine.get_time_from_utc(2024, 10, 2, 18, 49, 0)
    
    lux = moon_model.get_extraterrestrial_illuminance(t)
    phi = moon_model.calculate_phase_angle(t)
    phi_deg = np.degrees(phi)

    print(f"\n--- New Moon Test ---")
    print(f"Fázový úhel: {phi_deg:.4f}°")
    print(f"Intenzita:   {lux:.6f} lx")

    # Nov má fázový úhel blízko 180 stupňů (PI)
    assert phi_deg > 170.0
    
    # Jas by měl být malý, ale díky Earthshine měřitelný (cca 1e-4 až 1e-3 lux)
    assert lux > 0.0
    assert lux < 0.01

def test_opposition_surge_logic(moon_model):
    """
    Izolovaný test matematiky pro Opposition Surge (Eq 13).
    """
    # Úhel 0 stupňů -> Max surge (1.27 + 0.045 = 1.315)
    # Undeger: 1.27 - 0.045(|phi| - 1). Pro phi=0: 1.27 - 0.045(-1) = 1.315
    val_0 = moon_model._calculate_opposition_surge(0.0)
    assert val_0 > 1.3
    
    # Úhel 8 stupňů -> Žádný surge (1.0)
    val_8 = moon_model._calculate_opposition_surge(np.radians(8.0))
    assert val_8 == 1.0
