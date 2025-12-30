import swisseph as swe
from core_files.constants import nakshatra_lords,NAKSHATRAS,TITHIS,PAKSHA_NAMES

def get_nakshatra_lord(nakshatra_name: str) -> str:
    return nakshatra_lords.get(nakshatra_name, "Неизвестен")

# nakshatra_data.py


def get_lunar_details(jd_ut):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_ephe_path('.')

    # Солнечно-лунные координаты
    moon, _ = swe.calc_ut(jd_ut, swe.MOON)
    sun, _ = swe.calc_ut(jd_ut, swe.SUN)

    moon_long = (moon[0] - swe.get_ayanamsa_ut(jd_ut)) % 360
    sun_long = (sun[0] - swe.get_ayanamsa_ut(jd_ut)) % 360

    # --- Накшатра ---
    nakshatra_index = int(moon_long // (360 / 27))
    nakshatra_pada = int((moon_long % (360 / 27)) // ((360 / 27) / 4)) + 1

    # --- Титхи ---
    tithi_angle = (moon_long - sun_long) % 360
    tithi_index = int(tithi_angle // 12)
    paksha = "shukla" if tithi_index < 15 else "krishna"
    tithi_name = TITHIS[tithi_index % 15]

    return {
        "nakshatra": NAKSHATRAS[nakshatra_index],
        "nakshatra_number": nakshatra_index + 1,
        "nakshatra_pada": nakshatra_pada,
        "tithi": tithi_name,
        "tithi_number": tithi_index + 1,
        "paksha": PAKSHA_NAMES[paksha]
    }
