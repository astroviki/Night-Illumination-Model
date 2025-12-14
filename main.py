import datetime
import pytz
from src.illumination_model.scene import IlluminationScene

def main():
    # 1. Nastavení scény
    scene = IlluminationScene()
    
    # 2. Nastavení pozorovatele (např. Praha)
    lat = 50.0755
    lon = 14.4378
    elev = 200.0
    
    # 3. Nastavení času (Teď)
    # Použijeme časovou zónu pro správný převod
    prague_tz = pytz.timezone('Europe/Prague')
    now_local = datetime.datetime.now(prague_tz)
    
    # Převod na UTC pro Skyfield
    now_utc = now_local.astimezone(pytz.utc)
    
    # Vytvoření Skyfield času
    ts = scene.engine.ts
    t = ts.from_datetime(now_utc)
    
    # 4. Výpočet
    print(f"--- ANALÝZA OSVĚTLENÍ (Undeger Model 2009) ---")
    print(f"Lokace: Praha [{lat}, {lon}]")
    print(f"Čas:    {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("-" * 40)
    
    # Simulace pro různé počasí
    weather_conditions = {
        "Jasno (Hory)": 2.0,
        "Standardní": 3.0,
        "Mírný opar": 5.0,
        "Zataženo/Mlha": 20.0
    }
    
    for weather, turbidity in weather_conditions.items():
        result = scene.calculate_illumination(lat, lon, elev, t, turbidity)
        
        total = result['total_lux']
        sun = result['sun_lux']
        moon = result['moon_lux']
        stars = result['stars_lux']
        
        print(f"Počasí: {weather:<15} (T={turbidity})")
        print(f"  > CELKEM: {total:.5f} Lux")
        
        # Jednoduchá interpretace
        if total > 1000:
            desc = "Den (Jasno)"
        elif total > 100:
            desc = "Den (Zataženo/Šero)"
        elif total > 1:
            desc = "Soumrak / Svítání"
        elif total > 0.1:
            desc = "Noc (Úplněk)"
        else:
            desc = "Noc (Tma)"
            
        print(f"  > Stav:   {desc}")
        print(f"  > Zdroje: Slunce={sun:.5f}, Měsíc={moon:.5f}, Hvězdy={stars:.5f}")
        print("-" * 40)

    print("\nAstronomická data:")
    print(f"Slunce Elevace: {result['sun_altitude']:.2f}°")
    print(f"Měsíc Elevace:  {result['moon_altitude']:.2f}°")
    print(f"Měsíc Fáze:     {result['moon_phase_angle']:.2f}° (0=Full, 180=New)")

if __name__ == "__main__":
    main()
