# Real-time Outdoor Illumination Model (Python)

**Vědecký model pro výpočet venkovního osvětlení (Slunce, Měsíc, Hvězdy) a atmosférické extinkce v reálném čase.**

Tento projekt je moderní Python implementace algoritmů pro simulaci osvětlení, založená primárně na práci *C. Undeger (2009): Modeling Daytime and Night Illumination*, ale s významnými modernizacemi v oblasti astrometrie a fotometrie.

## 🚀 Klíčové vlastnosti

Oproti původnímu článku (2009) přináší tento model řadu vylepšení:

* **Přesná Astrometrie:** Místo aproximačních řad využívá knihovnu `Skyfield` a efemeridy NASA JPL DE421 (přesnost na zlomky úhlové vteřiny).
* **Fyzikální model Měsíce:**
    * **3D Fázový úhel:** Přesný vektorový výpočet fáze.
    * **Earthshine (Popelavý svit):** Implementován model odrazu Země -> Měsíc, což zajišťuje realistické (nenulové) osvětlení i při Novu.
    * **Opposition Surge:** Nelineární nárůst jasu při úplňku.
* **Atmosférický Model:**
    * **Robustní Air Mass:** Použití Kasten-Young/Rozenberg modelů, které nedivergují na horizontu (zvládá západ slunce).
    * **Proměnná Turbidita:** Možnost simulovat různé počasí (od hor po hustou mlhu).
* **Hvězdné pozadí:** Dynamický model hvězd, které podléhají atmosférické extinkci (v mlze "zhasnou").

## 📦 Instalace

Doporučujeme použít virtuální prostředí:

```bash
# Vytvoření prostředí
python3 -m venv .venv
source .venv/bin/activate

# Instalace projektu v editovatelném módu
pip install -e .
