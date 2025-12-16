
# Real-time Outdoor Illumination Model (Python)

**Scientific model for calculating outdoor illumination (Sun, Moon, Stars) and atmospheric extinction in real-time.**

[cite_start]This project is a modern Python implementation of illumination simulation algorithms[cite: 1], primarily based on the work *C. Undeger (2009): Modeling Daytime and Night Illumination*, but with significant modernizations in astrometry and photometry.

## 🚀 Key Features

Compared to the original paper (2009), this model introduces several improvements:

* **Precise Astrometry:** Uses `Skyfield` library and NASA JPL DE421 ephemerides instead of approximation series, ensuring sub-arcsecond precision.
* **Physical Moon Model:**
    * [cite_start]**3D Phase Angle:** Accurate vector-based phase calculation[cite: 1, 11].
    * **Earthshine:** Implements the reflection Earth -> Moon -> Earth, ensuring realistic (non-zero) illumination even during New Moon.
    * [cite_start]**Opposition Surge:** Non-linear brightness surge at Full Moon[cite: 11].
* **Atmospheric Model:**
    * [cite_start]**Robust Air Mass:** Uses Kasten-Young/Rozenberg models that do not diverge at the horizon (handles sunsets correctly)[cite: 16].
    * [cite_start]**Variable Turbidity:** Ability to simulate various weather conditions (from clear mountains to dense fog)[cite: 16].
* [cite_start]**Stellar Background:** Dynamic star model subject to atmospheric extinction (stars "disappear" in fog)[cite: 1, 3].

## 📦 Installation

We recommend using a virtual environment:

```bash
# Create environment
python3 -m venv .venv
source .venv/bin/activate

# Install project in editable mode
pip install -e .

## 📚 References

- Undeger, C. (2009). Modeling Daytime and Night Illumination. Middle East Technical University.

- JPL DE421 Ephemerides: NASA Jet Propulsion Laboratory.

- Kasten, F. and Young, A. T. (1989). Revised optical air mass tables and approximation formula.

##📄 License

MIT License
