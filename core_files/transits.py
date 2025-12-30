import swisseph as swe
from core_files.astro_report import get_planet_positions_and_houses  # твой базовый движок
from core_files.transit_analys import transit_aspect_analysis

# Устанавливаем сидерическую систему Лахири
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path(".")


def dms_str_to_float(dms_str):
    try:
        dms_str = dms_str.replace("'''", "''").strip()
        deg_part, rest = dms_str.split("°")

        # Разбиваем rest на минуты и секунды, при этом по первому апострофу:
        min_part, sec_part = rest.split("'", 1)  # maxsplit=1

        # Убираем все апострофы и пробелы из секунд
        sec_part = sec_part.replace("'", "").strip()

        deg = float(deg_part)
        minute = float(min_part)
        second = float(sec_part)

        return deg + minute / 60 + second / 3600
    except Exception as e:
        print(f"[ОШИБКА] Неверное значение градуса: '{dms_str}' или лагна: {e}")
        return None


def is_retrograde(jd_ut, planet_id):
    pos, ret_flag = swe.calc_ut(jd_ut, planet_id, swe.FLG_SPEED)
    speed = pos[3]
    return speed < 0


def calculate_transit_positions(jd_ut, latitude, longitude):
    """
    Рассчитать позиции транзитных планет на заданную дату,
    добавляя информацию о ретроградности.
    """
    transit_positions, _ = get_planet_positions_and_houses(jd_ut, latitude, longitude)

    # Добавляем метку ретроградности R для планет
    for planet, data in transit_positions.items():
        if planet in ["Раху", "Кету", "Лагна"]:
            continue  # Узлы и лагна не ретроградны
        planet_id = {
            "Солнце": swe.SUN,
            "Луна": swe.MOON,
            "Марс": swe.MARS,
            "Меркурий": swe.MERCURY,
            "Юпитер": swe.JUPITER,
            "Венера": swe.VENUS,
            "Сатурн": swe.SATURN,
        }.get(planet, None)

        if planet_id is not None:
            if is_retrograde(jd_ut, planet_id):
                data["degree"] += " R"  # Добавляем R для ретроградности

    return transit_positions


def calculate_house_for_transit(planet_degree, natal_lagna_degree):
    """
    Вычисляет дом транзитной планеты относительно натальной лагны.
    Возвращает None, если входные данные некорректны.
    """
    if planet_degree is None or natal_lagna_degree is None:
        return None
    try:
        asc_sign = int(natal_lagna_degree // 30) % 12
        planet_sign = int(planet_degree // 30) % 12
        house = (planet_sign - asc_sign) % 12 + 1
        return house
    except Exception as e:
        print(f"[ОШИБКА] calculate_house_for_transit: {e}")
        return None


def analyze_transit(natal_positions, natal_lagna_degree, jd_ut, latitude, longitude):
    """
    Полный анализ транзитов: позиции планет и аспекты.
    """
    transit_positions = calculate_transit_positions(jd_ut, natal_lagna_degree, latitude, longitude)
    aspects = transit_aspect_analysis(transit_positions, natal_positions, natal_lagna_degree)
    return {
        "transit_positions": transit_positions,
        "aspects": aspects
    }
