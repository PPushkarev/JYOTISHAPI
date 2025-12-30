import swisseph as swe
from datetime import datetime

from core_files.lunar_module import nakshatra_lords, NAKSHATRAS
from core_files.constants import VIMSHOTTARI_DURATIONS, YEAR_IN_DAYS, NAKSHATRA_LENGTH

NAKSHATRA_NAMES = NAKSHATRAS

def degree_str_to_float(degree_str: str) -> float:
    """
    Converts a string formatted as "26°43'38''" into a decimal degree (float).
    """
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

def calculate_fraction_in_nakshatra(degree_str: str, pada: int) -> float:
    """
    Calculates the consumed fraction of the Nakshatra based on degree and pada.
    """
    total_degrees = degree_str_to_float(degree_str)
    nakshatra_pos = total_degrees % NAKSHATRA_LENGTH
    # Accounting for position within the pada (each pada is 1/4 of a Nakshatra)
    pada_fraction_degrees = (pada - 1) * (NAKSHATRA_LENGTH / 4)
    precise_pos = nakshatra_pos + pada_fraction_degrees
    fraction = precise_pos / NAKSHATRA_LENGTH
    # Correct if position exceeds Nakshatra boundaries
    if fraction >= 1:
        fraction -= 1
    return fraction

def jd_to_date(jd):
    """
    Converts Julian Day to a Python date object.
    """
    y, m, d, _ = swe.revjul(jd)
    return datetime(y, m, d).date()

""" Core Logic """

def calculate_vimshottari_dasha_full(jd_birth: float, moon_data: dict):
    """
    Calculates the full sequence of Mahadashas starting from birth.
    """
    # Validate required fields
    if "degree" not in moon_data or "pada" not in moon_data:
        raise ValueError("В moon_data должны быть поля 'degree' и 'pada'")

    # Calculate precise position within the Nakshatra including pada
    fraction_in_nakshatra = calculate_fraction_in_nakshatra(moon_data["degree"], moon_data["pada"])

    nakshatra_name = moon_data.get("nakshatra")
    if nakshatra_name is None:
        raise ValueError("В moon_data отсутствует поле 'nakshatra'")

    # Determine Nakshatra Lord
    start_planet = nakshatra_lords.get(nakshatra_name)
    if start_planet is None:
        raise ValueError(f"Лорд накшатры '{nakshatra_name}' не найден.")

    planet_names = [p[0] for p in VIMSHOTTARI_DURATIONS]
    if start_planet not in planet_names:
        raise ValueError(f"Планета '{start_planet}' отсутствует в VIMSHOTTARI_DURATIONS.")

    start_index = planet_names.index(start_planet)
    start_planet_duration_days = VIMSHOTTARI_DURATIONS[start_index][1] * YEAR_IN_DAYS

    # Calculate Mahadasha start date by offsetting backwards from birth based on consumed fraction
    days_passed_in_current_dasha = fraction_in_nakshatra * start_planet_duration_days
    start_jd_current_dasha = jd_birth - days_passed_in_current_dasha

    current_start_jd = start_jd_current_dasha
    results = []

    # Iterate through all 9 planets in the sequence
    for i in range(9):
        dasha_index = (start_index + i) % 9
        dasha_planet, dasha_years = VIMSHOTTARI_DURATIONS[dasha_index]
        dasha_days = dasha_years * YEAR_IN_DAYS

        dasha_end_jd = current_start_jd + dasha_days

        results.append({
            "level": "dasha",
            "planet": dasha_planet,
            "start_jd": current_start_jd,
            "end_jd": dasha_end_jd,
            "duration_days": dasha_days,
            "start_date": jd_to_date(current_start_jd),
            "end_date": jd_to_date(dasha_end_jd),
        })

        current_start_jd = dasha_end_jd

    return results


def calculate_antara_dashas(mahadasha_planet, start_jd, end_jd):
    """
    Calculates Antardashas (sub-periods) within a given Mahadasha.
    """
    total_days = end_jd - start_jd
    antara_list = []

    # Get duration ratios for sub-periods
    mahadasha_years = dict(VIMSHOTTARI_DURATIONS)[mahadasha_planet]
    mahadasha_days = mahadasha_years * YEAR_IN_DAYS

    # Reorder planets to start with the Mahadasha planet
    planet_names = [p[0] for p in VIMSHOTTARI_DURATIONS]
    start_index = planet_names.index(mahadasha_planet)
    ordered_planets = VIMSHOTTARI_DURATIONS[start_index:] + VIMSHOTTARI_DURATIONS[:start_index]

    current_start_jd = start_jd

    for antara_planet, antara_years in ordered_planets:
        proportion = antara_years / 120
        duration_days = total_days * proportion
        end_jd = current_start_jd + duration_days

        antara_list.append({
            "level": "antara",
            "mahadasha": mahadasha_planet,
            "planet": antara_planet,
            "start_jd": current_start_jd,
            "end_jd": end_jd,
            "duration_days": duration_days,
            "start_date": jd_to_date(current_start_jd),
            "end_date": jd_to_date(end_jd),
        })

        current_start_jd = end_jd

    return antara_list


def calculate_pratyantara_dashas(mahadasha_planet, antara_planet, start_jd, end_jd):
    """
    Calculates Pratyantardashas (sub-sub-periods) within an Antardasha.
    """
    total_days = end_jd - start_jd
    pratyantara_list = []

    planet_names = [p[0] for p in VIMSHOTTARI_DURATIONS]
    start_index = planet_names.index(antara_planet)
    ordered_planets = VIMSHOTTARI_DURATIONS[start_index:] + VIMSHOTTARI_DURATIONS[:start_index]

    # Calculate proportions as a fraction of the Antardasha
    current_start_jd = start_jd

    for pratyantara_planet, pratyantara_years in ordered_planets:
        proportion = pratyantara_years / 120  # Standard ratio
        duration_days = total_days * proportion
        end_jd = current_start_jd + duration_days

        pratyantara_list.append({
            "level": "pratyantara",
            "mahadasha": mahadasha_planet,
            "antara": antara_planet,
            "planet": pratyantara_planet,
            "start_jd": current_start_jd,
            "end_jd": end_jd,
            "duration_days": duration_days,
            "start_date": jd_to_date(current_start_jd),
            "end_date": jd_to_date(end_jd),
        })

        current_start_jd = end_jd

    return pratyantara_list

def print_vimshottari_with_antara_and_pratyantara(jd_birth, moon_data):
    """
    Displays the Vimshottari periods including Maha, Antara, and Pratyantara levels.
    """
    mahadashas = calculate_vimshottari_dasha_full(jd_birth, moon_data)

    print("\n=== Вимшоттари — Маха / Антара / Прати-антара ===")
    for maha in mahadashas:
        maha_start = maha['start_date'].strftime("%Y-%m-%d")
        maha_end = maha['end_date'].strftime("%Y-%m-%d")
        print(f"\n🔷 Махадаша {maha['planet']} ({maha_start} — {maha_end})")

        antara_dashas = calculate_antara_dashas(maha['planet'], maha['start_jd'], maha['end_jd'])
        for antara in antara_dashas:
            antara_start = antara['start_date'].strftime("%Y-%m-%d")
            antara_end = antara['end_date'].strftime("%Y-%m-%d")
            print(f"  ├─ Антара {antara['planet']} ({antara_start} — {antara_end})")

            pratyantaras = calculate_pratyantara_dashas(
                maha['planet'], antara['planet'], antara['start_jd'], antara['end_jd']
            )

            for praty in pratyantaras:
                p_start = praty['start_date'].strftime("%Y-%m-%d")
                p_end = praty['end_date'].strftime("%Y-%m-%d")
                print(f"  │   └─ Прати-антара {praty['planet']:8} {p_start} — {p_end}")


def print_vimshottari_with_antara(jd_birth, moon_data):
    """
    Displays Mahadashas and Antardashas.
    """
    mahadashas = calculate_vimshottari_dasha_full(jd_birth, moon_data)

    print("\n=== Вимшоттари — Маха- и Антара-даши ===")
    for maha in mahadashas:
        print(f"\nМахадаша {maha['planet']} ({jd_to_date(maha['start_jd'])} — {jd_to_date(maha['end_jd'])})")
        print(f"{'Антара':8} | {'Начало':10} | {'Конец':10}")
        print("-" * 35)
        antara_dashas = calculate_antara_dashas(maha['planet'], maha['start_jd'], maha['end_jd'])
        for antara in antara_dashas:
            start = antara['start_date'].strftime("%Y-%m-%d")
            end = antara['end_date'].strftime("%Y-%m-%d")
            print(f"{antara['planet']:8} | {start} | {end}")


def print_all_vimshottari_periods(jd_birth, moon_data):
    """
    Prints all calculated Vimshottari data in a simple table.
    """
    dasha_data = calculate_vimshottari_dasha_full(jd_birth, moon_data)
    print("\n=== Все периоды Вимшоттари ===")
    print(f"{'Уровень':10} | {'Планета':8} | {'Начало':10} | {'Конец':10}")
    print("-" * 50)
    for period in dasha_data:
        start = period["start_date"].strftime("%Y-%m-%d")
        end = period["end_date"].strftime("%Y-%m-%d")
        print(f"{period['level']:10} | {period['planet']:8} | {start} | {end}")

def print_vimshottari_main_periods(jd_birth, moon_data):
    """
    Prints only the primary Mahadasha periods.
    """
    dasha_data = calculate_vimshottari_dasha_full(jd_birth, moon_data)
    print("\n=== Вимшоттари — основные периоды (Махадаша) ===")
    print(f"{'Планета':7} | {'Начало':10} | {'Конец':10}")
    print("-" * 33)

    main_periods = [p for p in dasha_data if p["level"] == "dasha"]

    for period in main_periods:
        start = period["start_date"].strftime("%Y-%m-%d")
        end = period["end_date"].strftime("%Y-%m-%d")
        print(f"{period['planet']:7} | {start} | {end}")



def find_active_period(periods, current_jd):
    """
    periods - list of dictionaries containing 'start_jd' and 'end_jd'
    current_jd - point in time (Julian Day)
    Returns the period dictionary containing current_jd, or None
    """
    for p in periods:
        if p['start_jd'] <= current_jd < p['end_jd']:
            return p
    return None


def get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data):
    """
    Determines active Maha, Antara, and Pratyantara dashas for a specific transit date.
    """
    # Calculate Mahadashas
    mahadashas = calculate_vimshottari_dasha_full(jd_birth, moon_data)
    # Find active Mahadasha based on transit date
    active_maha = find_active_period(mahadashas, jd_transit)
    if not active_maha:
        return None

    # Calculate Antardashas within the active Mahadasha
    antaradas = calculate_antara_dashas(active_maha['planet'], active_maha['start_jd'], active_maha['end_jd'])
    active_antara = find_active_period(antaradas, jd_transit)
    if not active_antara:
        return None

    # Calculate Pratyantardashas within the active Antardasha
    pratyantaradas = calculate_antara_dashas(active_antara['planet'], active_antara['start_jd'],
                                             active_antara['end_jd'])
    active_pratyantara = find_active_period(pratyantaradas, jd_transit)
    if not active_pratyantara:
        return None

    return {
        "mahadasha": active_maha,
        "antara": active_antara,
        "pratyantara": active_pratyantara,
    }


def print_vimshottari_report_for_date(jd_transit, jd_birth, moon_data):
    """
    Displays a report of active dashas for a specific date.
    """
    states = get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data)
    if not states:
        print("Не удалось определить даши для указанной даты.")
        return

    print(f"\n=== Вимшоттари даши на дату {jd_to_date(jd_transit)} ===")

    maha = states['mahadasha']
    antara = states['antara']
    pratyantara = states['pratyantara']

    print(f"Махадаша: {maha['planet']} ({jd_to_date(maha['start_jd'])} — {jd_to_date(maha['end_jd'])})")
    print(f"Антара: {antara['planet']} ({jd_to_date(antara['start_jd'])} — {jd_to_date(antara['end_jd'])})")
    print(
        f"Прайантарадаша (Пратьянтара): {pratyantara['planet']} ({jd_to_date(pratyantara['start_jd'])} — {jd_to_date(pratyantara['end_jd'])})")

def find_active_dashas(vimshottari_data, transit_date):
    """
    Searches for active Maha, Antara, and Pratyantara dashas for transit_date
    within pre-calculated Vimshottari data.
    """

    def find_period(periods, date):
        for period in periods:
            if period['start_date'] <= date <= period['end_date']:
                return period
        return None

    maha = find_period([vimshottari_data['mahadashas']], transit_date) \
        or find_period(vimshottari_data['mahadashas'], transit_date)

    if not maha:
        # Fallback for alternative data formats
        maha = find_period([vimshottari_data['mahadasha']], transit_date) \
            or find_period(vimshottari_data.get('mahadashas', []), transit_date)

    if not maha:
        return None, None, None

    antara = None
    pratyantara = None

    # Find Antardasha within Mahadasha
    if 'antaras' in maha:
        antara = find_period(maha['antaras'], transit_date)

    # Find Pratyantara within Antardasha
    if antara and 'pratyantaras' in antara:
        pratyantara = find_period(antara['pratyantaras'], transit_date)

    return maha, antara, pratyantara



def print_dashas(maha, antara, pratyantara):
    """
    Prints formatted transit dasha report.
    """
    if not maha:
        print("⚠️ Не удалось найти активные даши для этой даты.")
        return

    print("\n=== ВИМШОТТАРИ ДАША НА ДАТУ ТРАНЗИТА ===")
    print(f"Махадаша     : {maha['planet']}     ({maha['start_date'].strftime('%Y-%m-%d')} — {maha['end_date'].strftime('%Y-%m-%d')})")

    if antara:
        print(f"  ├─ Антарадаша : {antara['planet']}     ({antara['start_date'].strftime('%Y-%m-%d')} — {antara['end_date'].strftime('%Y-%m-%d')})")
    else:
        print("  ├─ Антарадаша : не найдена")

    if pratyantara:
        print(f"  │   └─ Пратьянтара: {pratyantara['planet']}     ({pratyantara['start_date'].strftime('%Y-%m-%d')} — {pratyantara['end_date'].strftime('%Y-%m-%d')})")
    else:
        print("  │   └─ Пратьянтара: не найдена")