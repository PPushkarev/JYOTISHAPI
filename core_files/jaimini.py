# jamini.py
from core_files.constants import CHARA_KARAKA_ORDER, EXCLUDED_PLANETS


def get_karakas_by_longitudes(planet_positions):
    """Назначает караки по долготам внутри знака (0–30°)"""
    usable = {k: v for k, v in planet_positions.items() if k not in EXCLUDED_PLANETS}
    inner_deg = [(name, pos % 30) for name, pos in usable.items()]
    sorted_inner = sorted(inner_deg, key=lambda x: x[1], reverse=True)
    return {planet: CHARA_KARAKA_ORDER[i] for i, (planet, _) in enumerate(sorted_inner)}

def format_degree(degree_float):
    """Форматирует градусы в вид 00°00'00''"""
    total_seconds = int(degree_float * 3600)
    deg = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{deg}°{minutes}'{seconds}''"

def get_planets_table_with_karakas(jd, lat, lon, lagna, get_planet_positions_and_houses):
    # Получаем данные по планетам
    planets = get_planet_positions_and_houses(jd, lat, lon, lagna)

    # Собираем долготы для карак
    planet_longitudes = {
        name: data['longitude'] for name, data in planets.items()
        if name not in ["Раху", "Кету", "Лагна"]
    }

    karakas = get_karakas_by_longitudes(planet_longitudes)

    # Заголовок
    header = (
        "=== ПЛАНЕТЫ И ДОМА ===\n"
        "Планета    | Карака | Градусы      | Знак     | Дом   | Накшатра (Пада)      | Управитель накшатры\n"
        + "-" * 95
    )

    rows = [header]

    for name in ["Лагна", "Солнце", "Луна", "Марс", "Меркурий", "Юпитер", "Венера", "Сатурн", "Раху", "Кету"]:
        data = planets.get(name)
        if not data:
            continue

        degree = format_degree(data["longitude"])
        rashi = data.get("sign", "-")
        house = data.get("house", "-")
        nak = data.get("nakshatra_name", "-")
        pada = data.get("nakshatra_pada", "-")
        lord = data.get("nakshatra_lord", "-")

        nakshatra_info = f"{nak} ({pada})"
        karaka = karakas.get(name, "-")

        row = f"{name:<10} | {karaka:^6} | {degree:<12} | {rashi:<8} | {house:<5} | {nakshatra_info:<20} | {lord}"
        rows.append(row)

    return "\n".join(rows)
