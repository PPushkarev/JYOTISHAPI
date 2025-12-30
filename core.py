import pytz
from datetime import datetime
from core_files.location_lookup import get_location_data
from core_files.russian_cities import get_city_info
from core_files.birth_chart_storage import save_birth_chart, list_birth_charts
from core_files.astro_report import get_planet_positions_and_houses  # Lagna is calculated internally
from core_files.lunar_module import nakshatra_lords
from core_files.jaimini import get_karakas_by_longitudes
from core_files.constants import HOUSE_MEANINGS
from core_files.transit_analys import analyze_transits_full, analyze_double_aspects_from_aspects, get_aspected_houses, \
    transit_aspect_analysis, get_house_rulers, evaluate_house_ruler, check_sade_sati
from core_files.vimshottari import print_vimshottari_main_periods, print_vimshottari_with_antara_and_pratyantara, \
    get_vimshottari_dasha_states, print_dashas
from core_files.constants import ZODIAC_SIGNS, nakshatra_name, NAKSHATRA_LENGTH
from core_files.arudha import calculate_arudha_table, get_nakshatra_and_pada_by_degree
from core_files.transit_analys import calculate_transit_positions
from core_files.transit_analys import analyze_transit_planets_detailed, format_transit_planets_detailed  # Import required
from core_files.vimshottari import print_vimshottari_with_antara

# --- Local utility functions ---

def degree_str_to_float(degree_str: str) -> float:
    """Parses a degree string (e.g., 10°20'30'') into a decimal float."""
    try:
        parts = degree_str.replace("''", "").split("°")
        deg = float(parts[0])
        min_sec = parts[1]
        minutes, seconds = min_sec.split("'")
        minutes = float(minutes)
        seconds = float(seconds)
        return deg + minutes / 60 + seconds / 3600
    except Exception as e:
        print(f"Ошибка при парсинге градусов '{degree_str}': {e}")
        return 0.0


def calculate_julian_day(dt: datetime, utc_offset: float) -> float:
    """Calculates Julian Day from local datetime and UTC offset using Swiss Ephemeris."""
    import swisseph as swe
    from datetime import timezone, timedelta

    dt_utc = dt.replace(tzinfo=timezone(timedelta(hours=utc_offset))).astimezone(pytz.utc)
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)
    return jd


def get_zodiac_sign(degree: float) -> str:
    """Returns the zodiac sign name for a given degree."""
    index = int(degree // 30)
    return ZODIAC_SIGNS[index]


def input_int(prompt: str, min_value: int, max_value: int) -> int:
    """Validates integer input from the user within a specific range."""
    while True:
        try:
            value = int(input(prompt).strip())
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Введите число от {min_value} до {max_value}.")
        except ValueError:
            print("Пожалуйста, введите корректное число.")


def get_nakshatra_and_pada_by_degree(degree: float):
    """Determines the Nakshatra and Pada for a given degree."""
    total_deg = degree % 360
    nak_index = int(total_deg // NAKSHATRA_LENGTH)
    pada = int((total_deg % NAKSHATRA_LENGTH) // (NAKSHATRA_LENGTH / 4)) + 1
    nak = nakshatra_name[nak_index]
    return nak, pada


# --- Natal Chart Creation Logic ---

def create_birth_chart():
    """Main process for collecting user data and creating a new birth chart."""
    print("Введите имя или псевдоним:")
    name = input("> ").strip()

    print("Введите год рождения (например, 1980):")
    year = input_int("> ", 1900, 2100)

    print("Введите месяц рождения (1-12):")
    month = input_int("> ", 1, 12)

    print("Введите день рождения (1-31):")
    day = input_int("> ", 1, 31)

    print("Введите час рождения (0-23):")
    hour = input_int("> ", 0, 23)

    print("Введите минуту рождения (0-59):")
    minute = input_int("> ", 0, 59)

    print("Введите город рождения (на русском языке):")
    city = input("> ").strip().lower()

    try:
        dt = datetime(year, month, day, hour, minute)
    except ValueError as e:
        print(f"Ошибка в дате или времени: {e}")
        return None

    # Determine coordinates and timezone using local data or API fallback
    city_info = get_city_info(city)
    if city_info:
        lat = city_info["latitude"]
        lon = city_info["longitude"]
        tz_name = city_info["timezone"]
    else:
        print("Город не найден в справочнике, пытаюсь определить по API...")
        try:
            loc_data = get_location_data(city, dt)
            lat = loc_data["latitude"]
            lon = loc_data["longitude"]
            tz_name = loc_data["timezone"]
        except Exception as e:
            print(f"Ошибка при определении местоположения: {e}")
            return None

    # Timezone localization and automatic UTC offset detection
    tz = pytz.timezone(tz_name)
    dt_localized = tz.localize(dt)
    auto_utc_offset = dt_localized.utcoffset().total_seconds() / 3600

    print(f"\nГород: {city.title()}")
    print(f"Широта: {lat}")
    print(f"Долгота: {lon}")
    print(f"Часовой пояс: {tz_name}")
    print(f"Дата и время рождения (локальное): {dt.strftime('%d.%m.%Y %H:%M')}")
    print(f"Автоматически определённое UTC-смещение: UTC{auto_utc_offset:+.0f}")

    user_input = input("Введите UTC-смещение вручную (например, +3) или нажмите Enter для подтверждения автоматического: ").strip()
    user_utc_offset = float(user_input) if user_input else auto_utc_offset
    print(f"Используемое UTC-смещение: UTC{user_utc_offset:+.0f}")

    jd = calculate_julian_day(dt, user_utc_offset)

    # Calculate planetary positions and houses
    planet_data, lagna_degree = get_planet_positions_and_houses(jd, lat, lon)

    # Convert degrees for Jaimini Karaka calculations
    planet_longitudes = {
        name: degree_str_to_float(data['degree']) for name, data in planet_data.items()
        if name not in ["Раху", "Кету", "Лагна"]
    }

    karakas = get_karakas_by_longitudes(planet_longitudes)
    sign = get_zodiac_sign(lagna_degree)

    # Display Natal Chart basic info
    print("\n=== НАТАЛЬНАЯ КАРТА ===")
    for planet, data in planet_data.items():
        nakshatra = data.get("nakshatra", "-")
        pada = data.get("pada", "-")
        nakshatra_lord = data.get("nakshatra_lord", "-")
        print(f"{planet:10} | {data['degree']:12} | {data['sign']:8} | {str(data['house']):5} | "
              f"{nakshatra} ({str(pada)}){' ' * (20 - len(nakshatra) - len(str(pada)) - 3)} | {nakshatra_lord}")

    print("\n=== РЕЗУЛЬТАТ ===")
    print(f"Юлианская дата (UTC): {jd:.5f}")
    print(f"Сидерическая лагна: {lagna_degree:.2f}° ({sign})")
    print("\n=== ПЛАНЕТЫ И ДОМА ===")
    header = f"{'Планета':12} | {'Карака':6} | {'Градусы':12} | {'Знак':8} | {'Дом':5} | {'Накшатра (Пада)':20} | {'Управитель накшатры'}"
    print(header)
    print("-" * len(header))

    for planet, data in planet_data.items():
        nakshatra = data.get("nakshatra", "-")
        pada = data.get("pada", "-")
        nakshatra_lord = data.get("nakshatra_lord", "-")
        spacing = 20 - len(nakshatra) - len(str(pada)) - 3
        karaka = karakas.get(planet, "-")

        display_name = planet
        if data.get("retrograde", False):
            display_name += " R"

        print(f"{display_name:12} | {karaka:^6} | {data['degree']:12} | {data['sign']:8} | {str(data['house']):5} | "
              f"{nakshatra} ({str(pada)}){' ' * spacing} | {nakshatra_lord}")

    print("\n=== АРУДХА-ПАДЫ (Arudha Padas) ===")
    print(f"{'Дом':3} | {'Метка':4} | {'Знак Арудхи':12} | {'Градусы':8} | {'Накшатра (Пада)':20}")
    print("-" * 60)

    lagna_sign_index = ZODIAC_SIGNS.index(sign)
    arudha_data = calculate_arudha_table(planet_data, lagna_sign_index)

    for entry in arudha_data:
        arudha_sign = entry['Знак Арудхи']
        sign_index = ZODIAC_SIGNS.index(arudha_sign)
        sign_start_deg = sign_index * 30.0

        nak, pada = get_nakshatra_and_pada_by_degree(sign_start_deg)

        print(f"{entry['Дом']:>3} | {entry['Метка']:4} | {arudha_sign:12} | {sign_start_deg:>8.2f}° | {nak} ({pada})")

    # Add longitude field for the Moon for Vimshottari Dasha calculations
    planet_data["Луна"]["longitude"] = degree_str_to_float(planet_data["Луна"]["degree"])

    print_vimshottari_main_periods(jd, planet_data["Луна"])
    print_vimshottari_with_antara(jd, planet_data["Луна"])
    print_vimshottari_with_antara_and_pratyantara(jd, planet_data["Луна"])


    # Construct and save the final chart dictionary
    chart_data = {
        "name": name,
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M"),
        "city": city.title(),
        "latitude": lat,
        "longitude": lon,
        "timezone": tz_name,
        "utc_offset": user_utc_offset,
        "julian_day": round(jd, 5),
        "lagna": round(lagna_degree, 2),
        "sign": sign,
        "planets": planet_data
    }

    save_birth_chart(chart_data)
    print(f"\nКарта сохранена для {name}.")



def calculate_moon_data(jd_birth, lat, lon):
    """Specific utility to get lunar degree, nakshatra, and pada."""
    import swisseph as swe

    # Calculate Moon position in degrees
    moon_pos, ret = swe.calc_ut(jd_birth, swe.MOON)[:2]
    # Calculate Nakshatra and Pada (moon_pos is 0-360)
    nakshatra, pada = get_nakshatra_and_pada_by_degree(moon_pos)

    degree_str = f"{int(moon_pos)}°{int((moon_pos % 1) * 60)}'{int((((moon_pos % 1) * 60) % 1) * 60)}''"

    return {
        "degree": degree_str,
        "nakshatra": nakshatra,
        "pada": pada,
        "retrograde": ret < 0,
        "longitude": moon_pos,
    }


def run_transit_analysis():
    """Menu logic for performing a daily transit analysis on a saved chart."""
    charts = list_birth_charts()
    if not charts:
        print("Нет сохранённых карт для анализа транзитов.")
        input("\nНажмите Enter...")
        return

    print("\nВыберите карту для анализа транзитов:")
    for idx, chart in enumerate(charts, 1):
        print(f"{idx}. {chart.get('name', f'Карта {idx}')}")

    choice = int(input("> "))
    selected_chart = charts[choice - 1]

    natal_positions = selected_chart.get("planets")
    natal_lagna_degree = selected_chart.get("lagna")
    lat = selected_chart.get("latitude")
    lon = selected_chart.get("longitude")

    transit_date_str = input("\nВведите дату транзита (ГГГГ-ММ-ДД): ").strip()
    transit_date = datetime.strptime(transit_date_str, "%Y-%m-%d")

    jd_transit = calculate_julian_day(transit_date, 0.0)
    transit_positions = calculate_transit_positions(jd_transit, natal_lagna_degree, lat, lon)

    # Core Transit Analysis
    report, houses_analysis = analyze_transits_full(natal_positions, transit_positions)

    def transit_aspect_analysis(transit_positions, natal_positions):
        """Internal helper for calculating planetary aspects for transits."""
        result = []
        for planet, data in transit_positions.items():
            current_house = data.get("house")
            if current_house is None:
                continue
            houses_aspected = get_aspected_houses(planet, current_house)
            for h in houses_aspected:
                result.append({
                    "transit_planet": planet,
                    "natal_house": h
                })
        return result

    aspects_data = transit_aspect_analysis(transit_positions, natal_positions)
    double_aspects = analyze_double_aspects_from_aspects(transit_positions, aspects_data)

    print("\n=== СОСТОЯНИЕ УПРАВИТЕЛЕЙ ДОМОВ ===")
    planet_house_map = {p: d["house"] for p, d in natal_positions.items() if "house" in d}
    house_rulers = get_house_rulers(natal_positions, transit_positions)

    for house_num in range(1, 13):
        ruler_data = house_rulers.get(house_num)
        if ruler_data:
            ruler, transit_house = ruler_data
            if ruler:
                result = evaluate_house_ruler(ruler, planet_house_map, transit_positions)
                print(f"Дом {house_num} — управитель {ruler}:")
                print(f"  Управитель {house_num} дома ({ruler}) в транзитном доме: {transit_house}")
            else:
                print(f"Дом {house_num}: управитель не определён\n")
        else:
            print(f"Дом {house_num}: данные отсутствуют\n")

    print("\n=== АНАЛИЗ КАЖДОЙ ТРАНЗИТНОЙ ПЛАНЕТЫ ===")
    detailed_analysis = analyze_transit_planets_detailed(transit_positions)
    print(format_transit_planets_detailed(detailed_analysis))

    jd_transit = calculate_julian_day(transit_date, 0.0)
    transit_positions = calculate_transit_positions(jd_transit, natal_lagna_degree, lat, lon)

    sade_sati_report = check_sade_sati(transit_positions, natal_positions)
    if sade_sati_report:
        print("\n=== ОТЧЁТ ПО САДЕ САТИ ===")
        print(sade_sati_report)
    else:
        print("\n=== Саде Сати в этот день не активна ===")

    report, houses_analysis = analyze_transits_full(natal_positions, transit_positions)

    if double_aspects:
        print("\n=== ДВОЙНЫЕ АСПЕКТЫ: ЮПИТЕР & САТУРН ===")
        for key, messages in double_aspects.items():
            if key == "same_sign":
                print(f"• {' '.join(messages)}")
            else:
                print(f"Дом {key}:")
                for msg in messages:
                    print(f"  - {msg}")

    print("\n=== ПОДРОБНЫЙ АНАЛИЗ ТРАНЗИТОВ ===")
    print(report)

    def interpret_score(score: int) -> str:
        """Translates numerical influence scores into readable results."""
        if score >= 2:
            return "Очень благоприятно"
        elif score == 1:
            return "Благоприятно"
        elif score == 0:
            return "Нейтрально"
        elif score == -1:
            return "Напряжённо"
        else:
            return "Неблагоприятно"

    print("\n=== СВОДНАЯ ТАБЛИЦА ВЛИЯНИЯ ПО ДОМАМ ===")
    header = f"{'Дом':>3} | {'Тема':28} | {'Баллы':>6} | {'Вывод'}"
    print(header)
    print("-" * len(header))

    for house_num in range(1, 13):
        house_data = houses_analysis.get(house_num, {})
        score = house_data.get("total_score", 0)
        theme = HOUSE_MEANINGS.get(house_num, "—")
        summary = interpret_score(score)
        print(f"{house_num:>3} | {theme:28} | {score:>6} | {summary}")

    print("\n=== ТРАНЗИТЫ НА ДАТУ ===")
    header = f"{'Планета':12} | {'Градусы':12} | {'Знак':8} | {'Дом':4} | {'Накшатра (Пада)':20} | {'R?':4} | {'Упр. накшатры'}"
    print(header)
    print("-" * len(header))

    for planet, data in transit_positions.items():
        deg = data.get("degree", "-")
        sign = data.get("sign", "-")
        house = str(data.get("house", "-"))
        nakshatra = data.get("nakshatra", "-")
        pada = data.get("pada", "-")
        retro = "R" if data.get("retrograde", False) else "-"
        lord = nakshatra_lords.get(nakshatra, "-")

        spacing = 20 - len(nakshatra) - len(str(pada)) - 3
        print(
            f"{planet:12} | {deg:12} | {sign:8} | {house:4} | {nakshatra} ({pada}){' ' * spacing} | {retro:^4} | {lord}"
        )

    jd_birth = selected_chart.get("julian_day")
    moon_data = selected_chart.get("planets", {}).get("Луна")

    if jd_birth is None or moon_data is None:
        print("\nНедостаточно данных для расчёта вимшоттари даши (нет даты рождения или данных Луны).")
    else:
        states = get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data)
        if states is None:
            print("\nНе удалось определить активные даши для данной даты транзита.")
        else:
            print("\n=== АКТИВНЫЕ ПЕРИОДЫ ВИМШОТТАРИ НА ДАТУ ТРАНЗИТА ===")
            print_dashas(states['mahadasha'], states['antara'], states['pratyantara'])

    input("\nНажмите Enter...")
    return report


def run_monthly_transit_analysis():
    """Menu logic for performing transit analysis for a full month."""
    charts = list_birth_charts()
    if not charts:
        print("Нет сохранённых карт для анализа транзитов.")
        input("\nНажмите Enter...")
        return

    print("\nВыберите карту для анализа транзитов на месяц:")
    for idx, chart in enumerate(charts, 1):
        print(f"{idx}. {chart.get('name', f'Карта {idx}')}")

    choice = int(input("> "))
    selected_chart = charts[choice - 1]

    natal_positions = selected_chart.get("planets")
    natal_lagna_degree = selected_chart.get("lagna")
    lat = selected_chart.get("latitude")
    lon = selected_chart.get("longitude")

    year = input_int("Введите год для анализа (например, 2025): ", 1900, 2100)
    month = input_int("Введите месяц для анализа (1-12): ", 1, 12)

    from calendar import monthrange
    days_in_month = monthrange(year, month)[1]

    daily_reports = []
    houses_scores = {h: 0 for h in range(1, 13)}
    houses_counts = {h: 0 for h in range(1, 13)}

    print(f"\nЗапускаем анализ транзитов с {year}-{month:02d}-01 по {year}-{month:02d}-{days_in_month}")

    # Loop through each day of the selected month
    for day in range(1, days_in_month + 1):
        transit_date = datetime(year, month, day)
        jd_transit = calculate_julian_day(transit_date, 0.0)
        transit_positions = calculate_transit_positions(jd_transit, natal_lagna_degree, lat, lon)
        report, houses_analysis = analyze_transits_full(natal_positions, transit_positions)

        for house_num in range(1, 13):
            house_data = houses_analysis.get(house_num, {})
            score = house_data.get("total_score", 0)
            houses_scores[house_num] += score
            if score != 0:
                houses_counts[house_num] += 1

        daily_reports.append({
            "date": transit_date.strftime("%Y-%m-%d"),
            "report": report,
            "houses_analysis": houses_analysis,
            "transit_positions": transit_positions,
            "jd_transit": jd_transit,
        })

    # Calculate average scores for the month
    average_scores = {}
    for h in range(1, 13):
        if houses_counts[h] > 0:
            average_scores[h] = houses_scores[h] / houses_counts[h]
        else:
            average_scores[h] = 0

    def interpret_score(score: float) -> str:
        """Translates average numerical scores into readable results."""
        if score >= 2:
            return "Очень благоприятно"
        elif 1 <= score < 2:
            return "Благоприятно"
        elif -1 < score < 1:
            return "Нейтрально"
        elif -2 < score <= -1:
            return "Напряжённо"
        else:
            return "Неблагоприятно"

    print("\n=== ИТОГОВЫЙ АНАЛИЗ ТРАНЗИТОВ ЗА МЕСЯЦ ===")
    header = f"{'Дом':>3} | {'Тема':28} | {'Средний балл':>12} | {'Интерпретация'}"
    print(header)
    print("-" * len(header))

    for house_num in range(1, 13):
        theme = HOUSE_MEANINGS.get(house_num, "—")
        avg_score = average_scores[house_num]
        interp = interpret_score(avg_score)
        print(f"{house_num:>3} | {theme:28} | {avg_score:12.2f} | {interp}")

    print("\n=== КЛЮЧЕВЫЕ ДАТЫ С ВЫСОКИМ ВЛИЯНИЕМ ===")
    for day_report in daily_reports:
        date = day_report["date"]
        high_influence_houses = [h for h, data in day_report["houses_analysis"].items()
                                 if data.get("total_score", 0) >= 2]
        if high_influence_houses:
            houses_str = ", ".join(str(h) for h in high_influence_houses)
            print(f"{date}: Высокое влияние в домах {houses_str}")

    # --- Detailed analysis for the last day of the month ---
    print("\n=== ПОДРОБНЫЙ АНАЛИЗ ПОСЛЕДНЕГО ДНЯ МЕСЯЦА ===")
    last_day_report = daily_reports[-1]
    transit_positions = last_day_report["transit_positions"]
    jd_transit = last_day_report["jd_transit"]

    # House Rulers
    house_rulers = get_house_rulers(natal_positions, transit_positions)
    print("\n=== СОСТОЯНИЕ УПРАВИТЕЛЕЙ ДОМОВ ===")
    for house_num in range(1, 13):
        ruler_data = house_rulers.get(house_num)
        if ruler_data:
            ruler, transit_house = ruler_data
            if ruler:
                print(f"Дом {house_num} — управитель {ruler}:")
                print(f"  Управитель {house_num} дома ({ruler}) в транзитном доме: {transit_house}")
            else:
                print(f"Дом {house_num}: управитель не определён")
        else:
            print(f"Дом {house_num}: данные отсутствуют")

    # Transit planet analysis
    print("\n=== АНАЛИЗ КАЖДОЙ ТРАНЗИТНОЙ ПЛАНЕТЫ ===")
    detailed_analysis = analyze_transit_planets_detailed(transit_positions)
    print(format_transit_planets_detailed(detailed_analysis))

    # Jupiter & Saturn double aspects
    aspects_data = transit_aspect_analysis(transit_positions, natal_positions)
    double_aspects = analyze_double_aspects_from_aspects(transit_positions, aspects_data)
    if double_aspects:
        print("\n=== ДВОЙНЫЕ АСПЕКТЫ: ЮПИТЕР & САТУРН ===")
        for key, messages in double_aspects.items():
            if key == "same_sign":
                print(f"• {' '.join(messages)}")
            else:
                print(f"Дом {key}:")
                for msg in messages:
                    print(f"  - {msg}")

    # Transit positions table
    print("\n=== ТРАНЗИТЫ НА ДАТУ ===")
    header = f"{'Планета':12} | {'Градусы':12} | {'Знак':8} | {'Дом':4} | {'Накшатра (Пада)':20} | {'R?':4} | {'Упр. накшатры'}"
    print(header)
    print("-" * len(header))
    for planet, data in transit_positions.items():
        deg = data.get("degree", "-")
        sign = data.get("sign", "-")
        house = str(data.get("house", "-"))
        nakshatra = data.get("nakshatra", "-")
        pada = data.get("pada", "-")
        retro = "R" if data.get("retrograde", False) else "-"
        lord = nakshatra_lords.get(nakshatra, "-")
        spacing = 20 - len(nakshatra) - len(str(pada)) - 3
        print(
            f"{planet:12} | {deg:12} | {sign:8} | {house:4} | {nakshatra} ({pada}){' ' * spacing} | {retro:^4} | {lord}"
        )

    # Sade Sati
    sade_sati_report = check_sade_sati(transit_positions, natal_positions)
    print("\n=== ОТЧЁТ ПО САДЕ САТИ ===")
    print(sade_sati_report if sade_sati_report else "Саде Сати не активна на данный момент.")

    # Vimshottari Dasha
    jd_birth = selected_chart.get("julian_day")
    moon_data = selected_chart.get("planets", {}).get("Луна")
    if jd_birth and moon_data:
        states = get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data)
        if states:
            print("\n=== АКТИВНЫЕ ПЕРИОДЫ ВИМШОТТАРИ НА ДАТУ ТРАНЗИТА ===")
            print_dashas(states['mahadasha'], states['antara'], states['pratyantara'])
        else:
            print("\nНе удалось определить активные даши.")
    else:
        print("\nНедостаточно данных для расчёта вимшоттари даши.")

    input("\nНажмите Enter...")


def main_menu():
    """Main CLI navigation menu."""
    while True:
        print("\nВыберите действие:")
        print("1 - Создать новую натальную карту")
        print("2 - Просмотреть список сохранённых карт")
        print("3 - Анализ транзитов на день")
        print("4 - Анализ транзита на месц")
        print("5 - Выход")

        choice = input("> ").strip()
        if choice == "1":
            create_birth_chart()
        elif choice == "2":
            list_birth_charts()
        elif choice == "3":
            run_transit_analysis()
        elif choice == "4":
            run_monthly_transit_analysis()
        elif choice == "5":
            print("Выход.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")



if __name__ == "__main__":
    main_menu()



def analyze_dashas_on_transit_date(chart_data, transit_date):
    """Calculates active Dasha periods for a specific transit date."""
    jd_birth = chart_data["julian_day"]
    moon_data = chart_data["planets"]["Луна"]

    # Convert transit date to Julian Day
    jd_transit = calculate_julian_day(transit_date, 0.0)

    # Fetch active Maha/Antara/Pratyantara periods
    states = get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data)
    if states is None:
        print("Не удалось определить даши для указанной даты.")
        return

    # Display results
    print_dashas(states['mahadasha'], states['antara'], states['pratyantara'])