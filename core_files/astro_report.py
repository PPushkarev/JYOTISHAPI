import swisseph as swe
from math import floor
from core_files.lunar_module import nakshatra_lords, get_nakshatra_lord
from core_files.constants import ZODIAC_SIGNS, nakshatra_name

# Устанавливаем сидерическую систему Лахири
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path(".")


def get_nakshatra_and_pada(degree):
    nakshatra_index = int(degree // (360 / 27))
    pada = int(((degree % (360 / 27)) // ((360 / 27) / 4))) + 1
    return nakshatra_name[nakshatra_index], pada


def deg_to_dms(deg_float):
    deg = floor(deg_float)
    minutes_float = (deg_float - deg) * 60
    minutes = floor(minutes_float)
    seconds = round((minutes_float - minutes) * 60)
    return deg, minutes, seconds


def deg_to_dms_within_house(planet_deg, house_start_deg):
    relative_deg = (planet_deg - house_start_deg) % 30
    deg = floor(relative_deg)
    minutes_float = (relative_deg - deg) * 60
    minutes = floor(minutes_float)
    seconds = round((minutes_float - minutes) * 60)
    return deg, minutes, seconds


def get_zodiac_sign(degree):
    sign_index = int(degree // 30) % 12
    return ZODIAC_SIGNS[sign_index]


def get_house_whole_sign(planet_degree, ascendant_degree):
    asc_sign = int(ascendant_degree // 30) % 12
    planet_sign = int(planet_degree // 30) % 12
    house = (planet_sign - asc_sign) % 12 + 1
    return house


def calculate_lagna_sidereal(jd_ut, latitude, longitude):
    house_cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P')
    asc_tropical = ascmc[0]
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    asc_sidereal = asc_tropical - ayanamsa
    if asc_sidereal < 0:
        asc_sidereal += 360
    return asc_sidereal, house_cusps


def get_planet_positions_and_houses(jd_ut, latitude, longitude):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_ephe_path('.')  # путь к эфемеридам

    lagna, _ = calculate_lagna_sidereal(jd_ut, latitude, longitude)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    planets = {
        "Лагна": None,
        "Солнце": swe.SUN,
        "Луна": swe.MOON,
        "Марс": swe.MARS,
        "Меркурий": swe.MERCURY,
        "Юпитер": swe.JUPITER,
        "Венера": swe.VENUS,
        "Сатурн": swe.SATURN,
        "Раху": swe.MEAN_NODE,
        "Кету": -swe.MEAN_NODE
    }

    results = {}

    # Обработка Лагны (Асцендента)
    house_start = (int(lagna // 30)) * 30
    deg, minute, sec = deg_to_dms_within_house(lagna, house_start)
    sign = get_zodiac_sign(lagna)
    nakshatra, pada = get_nakshatra_and_pada(lagna)
    lord = nakshatra_lords.get(nakshatra, "Неизвестен")

    results["Лагна"] = {
        "degree": f"{deg}°{minute}'{sec}''",
        "sign": sign,
        "house": 1,
        "nakshatra": nakshatra,
        "pada": pada,
        "nakshatra_lord": lord,
        "retrograde": False,  # Асцендент не бывает ретроградным
        "display_name": "Лагна"
    }

    for name, planet_id in planets.items():
        if name == "Лагна":
            continue

        if planet_id >= 0:
            data, flag = swe.calc_ut(jd_ut, planet_id)
            lon = data[0]
            speed = data[3]  # скорость по долготе
            is_retrograde = speed < 0
        else:
            # Для Кету берём противоположный узел
            data, flag = swe.calc_ut(jd_ut, swe.MEAN_NODE)
            lon = (data[0] + 180) % 360
            speed = data[3]
            is_retrograde = speed < 0

        sid_lon = lon - ayanamsa
        if sid_lon < 0:
            sid_lon += 360

        house = get_house_whole_sign(sid_lon, lagna)
        house_start = ((int(lagna // 30) + house - 1) % 12) * 30
        deg, minute, sec = deg_to_dms_within_house(sid_lon, house_start)
        sign = get_zodiac_sign(sid_lon)
        nakshatra, pada = get_nakshatra_and_pada(sid_lon)
        lord = nakshatra_lords.get(nakshatra, "Неизвестен")

        display_name = name + (" R" if is_retrograde else "")

        results[name] = {
            "degree": f"{deg}°{minute}'{sec}''",
            "sign": sign,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada,
            "nakshatra_lord": lord,
            "retrograde": is_retrograde,
            "display_name": display_name
        }

    return results, lagna

