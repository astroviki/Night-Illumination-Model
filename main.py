import datetime
import pytz
from src.illumination_model.scene import IlluminationScene

def main():
    # 1. Scene Setup
    scene = IlluminationScene()
    
    # 2. Observer Location (e.g., Prague)
    lat = 50.0755
    lon = 14.4378
    elev = 200.0
    
    # 3. Time Setup (Now)
    # Using timezone for correct conversion
    prague_tz = pytz.timezone('Europe/Prague')
    now_local = datetime.datetime.now(prague_tz)
    
    # Convert to UTC for Skyfield
    now_utc = now_local.astimezone(pytz.utc)
    
    # Create Skyfield Time object
    ts = scene.engine.ts
    t = ts.from_datetime(now_utc)
    
    # 4. Calculation
    print(f"--- ILLUMINATION ANALYSIS (Undeger Model 2009) ---")
    print(f"Location: Prague [{lat}, {lon}]")
    print(f"Time:    {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("-" * 40)
    
    # Simulace pro různé počasí
    weather_conditions = {
        "Clear (Mountains)": 2.0,
        "Standard": 3.0,
        "Light Haze": 5.0,
        "Overcast/Fog": 20.0
    }
    
    for weather, turbidity in weather_conditions.items():
        result = scene.calculate_illumination(lat, lon, elev, t, turbidity)
        
        total = result['total_lux']
        sun = result['sun_lux']
        moon = result['moon_lux']
        stars = result['stars_lux']
        
        print(f"Weather: {weather:<15} (T={turbidity})")
        print(f"  > TOTAL: {total:.5f} Lux")
        
        # Simple interpretation
        if total > 1000:
            desc = "Day (Bright)"
        elif total > 100:
            desc = "Day (Overcast/Dark)"
        elif total > 1:
            desc = "Twilight"
        elif total > 0.1:
            desc = "Night (Full Moon)"
        else:
            desc = "Night (Dark)"
            
        print(f"  > Status:   {desc}")
        print(f"  > Sources: Sun={sun:.5f}, Moon={moon:.5f}, Stars={stars:.5f}")
        print("-" * 40)

    print("\nAstronomical data:")
    print(f"Sun Elevation: {result['sun_altitude']:.2f}°")
    print(f"Moon Elevation:  {result['moon_altitude']:.2f}°")
    print(f"Moon phase:     {result['moon_phase_angle']:.2f}° (0=Full, 180=New)")

if __name__ == "__main__":
    main()
