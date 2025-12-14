import pytest
from illumination_model.atmosphere import AtmosphereModel

@pytest.fixture
def atmos():
    return AtmosphereModel()

def test_air_mass_zenith(atmos):
    """V zenitu (90 stupňů) by měl být Air Mass (m) roven 1.0."""
    m = atmos._calculate_air_mass(90.0)
    assert 0.99 < m < 1.01

def test_air_mass_horizon(atmos):
    """
    Na horizontu je dráha atmosférou násobně delší.
    Typicky m ~ 38 pro čistý horizont.
    """
    m = atmos._calculate_air_mass(0.0)
    assert 30.0 < m < 40.0

def test_extinction_values(atmos):
    """
    Ověření, zda extinkční koeficient odpovídá Tabulce 1 v článku.
    Pro čistou oblohu (Clear Sky, Turbidita ~2-3) by C mělo být cca 0.21.
    """
    # Turbidita 2.2 odpovídá velmi čisté obloze
    c_clean = atmos.calculate_extinction_coefficient(turbidity=2.2)
    print(f"\nExtinction (T=2.2): {c_clean}")
    
    # Článek uvádí pro Clear Sky C=0.21 [cite: 176]
    assert 0.18 < c_clean < 0.25

def test_transmittance_reduction(atmos):
    """Testuje, že více 'bordelu' v atmosféře snižuje světlo."""
    alt = 45.0 # Slunce v půlce
    
    # Čistá obloha (T=2)
    trans_clean = atmos.get_transmittance(alt, turbidity=2.0)
    
    # Znečištěná obloha (T=10)
    trans_haze = atmos.get_transmittance(alt, turbidity=10.0)
    
    print(f"\nTransmittance Clean: {trans_clean}")
    print(f"Transmittance Haze:  {trans_haze}")
    
    assert trans_clean > trans_haze
    assert trans_clean < 1.0 # Nikdy nepropustí 100%
