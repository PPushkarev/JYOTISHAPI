import swisseph as swe
from core_files.astro_report import get_house_whole_sign, deg_to_dms_within_house, get_nakshatra_and_pada, get_zodiac_sign
from core_files.constants import (
    benefic_planets,
    malefic_planets,
    dusthana_houses,
    kendra_houses,
    trikon_houses,
    DRISHTI_MAP,
    SIGN_RULERS,
    enemy_signs_map,
    friendly_signs_map, HOUSE_MEANINGS
)

planet_id_map = {
    "Солнце": swe.SUN,
    "Луна": swe.MOON,
    "Марс": swe.MARS,
    "Меркурий": swe.MERCURY,
    "Юпитер": swe.JUPITER,
    "Венера": swe.VENUS,
    "Сатурн": swe.SATURN,
    "Раху": None,
    "Кету": None,
    "Лагна": None,
}

def calculate_drishti(planet_name, current_house):
    """
    Возвращает список домов, которые аспектирует планета согласно правилам дришти.
    Коррекция: отсчёт аспектируемых домов начинается с текущего дома.
    """


    offsets = DRISHTI_MAP.get(planet_name, [7])
    # Исправленная строка — отсчёт начинается с текущего дома:
    drishti_houses = [((current_house + offset - 2) % 12) + 1 for offset in offsets]
    return drishti_houses

def transit_aspect_analysis(transit_positions, natal_positions=None):
    """
    Анализ аспектов транзитных планет только на другие транзитные планеты.
    Натальные планеты игнорируются.
    """
    aspects = []
    for t_planet_1, data_1 in transit_positions.items():
        house_1 = data_1.get("house")
        if house_1 is None:
            continue
        drishti_houses = calculate_drishti(t_planet_1, house_1)

        for t_planet_2, data_2 in transit_positions.items():
            if t_planet_1 == t_planet_2:
                continue  # планета не аспектирует сама себя
            house_2 = data_2.get("house")
            if house_2 is None:
                continue
            if house_2 in drishti_houses:
                aspects.append({
                    "transit_planet": t_planet_1,
                    "transit_house": house_1,
                    "natal_planet": t_planet_2,  # тут лучше переименовать в "target_planet"
                    "natal_house": house_2,
                    "aspect_type": "дришти",
                    "description": f"{t_planet_1} в доме {house_1} аспектирует {t_planet_2} в доме {house_2}"
                })
    return aspects


def group_aspects_by_house(aspects):
    """
    Собирает описание аспектов дришти для каждого дома,
    чтобы выводить их в анализе дома.
    """
    aspects_by_house = {h: [] for h in range(1, 13)}
    for asp in aspects:
        house = asp["natal_house"]
        planet = asp["transit_planet"]
        desc = asp["description"]
        aspects_by_house[house].append(f"{planet}: {desc}")
    return aspects_by_house

def get_transit_planets_aspecting_houses(transit_positions):
    """
    Для каждого дома возвращает список транзитных планет,
    которые делают дришти (аспектируют) этот дом.
    """
    aspect_map = {h: [] for h in range(1, 13)}
    for t_planet, t_data in transit_positions.items():
        t_house = t_data.get("house")
        if t_house is None:
            continue
        drishti_houses = calculate_drishti(t_planet, t_house)
        for h in drishti_houses:
            aspect_map[h].append(t_planet)
    return aspect_map

def calculate_transit_positions(jd_ut, natal_lagna_degree, latitude, longitude):
    """
    Расчёт положения транзитных планет в сидерическом зодиаке, их домов, накшатр и ретроградности.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_ephe_path('.')

    lagna = natal_lagna_degree
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    planets = {
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

    for name, planet_id in planets.items():
        if planet_id is not None and planet_id >= 0:
            data, flag = swe.calc_ut(jd_ut, planet_id)
            lon = data[0]
            speed = data[3]
            is_retrograde = speed < 0
        else:
            # Для Кету берем противоположность Раху
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
        degree_str = f"{deg}°{minute}'{sec}''"
        sign = get_zodiac_sign(sid_lon)
        nakshatra, pada = get_nakshatra_and_pada(sid_lon)

        results[name] = {
            "degree": degree_str,
            "sign": sign,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada,
            "retrograde": is_retrograde
        }

    return results

def evaluate_planet_in_house(planet, house):
    """
    Оценивает качество планеты по её положению в доме.
    Возвращает строку с оценкой влияния.
    """
    if house not in range(1, 13):
        return f"Ошибка: дом {house} вне допустимого диапазона (1–12)."
    if house in dusthana_houses:
        return f"{planet} в доме {house}: {'вредная' if planet in malefic_planets else 'благоприятная'} планета в Дустхане."
    if house in trikon_houses:
        return f"{planet} в доме {house}: {'благоприятная' if planet in benefic_planets else 'вредная'} планета в Триконе."
    if house in kendra_houses:
        return f"{planet} в доме {house}: {'благоприятная' if planet in benefic_planets else 'вредная'} планета в Кендре."
    return f"{planet} в доме {house}: нейтральное или смешанное влияние."

def wrap(house_number):
    """
    Округляет номер дома в пределах 1-12 (круговой цикл домов).
    """
    return (house_number - 1) % 12 + 1

def get_aspected_houses(planet_name, current_house):
    """
    Возвращает список домов, которые аспектирует планета, используя DRISHTI_MAP.
    """
    offsets = DRISHTI_MAP.get(planet_name, [7])
    return [wrap(current_house + o) for o in offsets]

def evaluate_house_aspects(planet_positions, house_rulers_map=None):
    """
    Для каждого дома возвращает словарь с планетами и их баллами (+1 или -1),
    исключая аспекты управителя на свой дом.
    """
    scores = {i: {} for i in range(1, 13)}  # дом: {планета: балл}

    for planet, house in planet_positions.items():
        score_for_planet = 1 if planet in benefic_planets else -1 if planet in malefic_planets else 0
        if score_for_planet == 0:
            continue

        aspect_houses = get_aspected_houses(planet, house)
        for h in aspect_houses:
            # исключаем ситуацию, когда планета — управитель h-го дома
            if house_rulers_map:
                if house_rulers_map.get(h) == planet:
                    continue
            scores[h][planet] = score_for_planet

    return scores



def analyze_double_aspects_from_aspects(transit_positions, aspects_data):
    """
    Анализ двойных аспектов между Сатурном и Юпитером,
    используя список аспектов aspects_data — каждый элемент с ключами:
    'transit_planet' и 'natal_house'.

    Возвращает словарь с домами и описаниями.
    """

    # Сбор аспектируемых домов по каждой планете
    aspects_dict = {}
    for asp in aspects_data:
        # asp — словарь, ожидаем ключи "transit_planet" и "natal_house"
        planet = asp.get("transit_planet")
        house = asp.get("natal_house")
        if planet is not None and house is not None:
            aspects_dict.setdefault(planet, []).append(house)

    saturn_house = transit_positions.get("Сатурн", {}).get("house")
    jupiter_house = transit_positions.get("Юпитер", {}).get("house")

    if saturn_house is None or jupiter_house is None:
        # Если у Сатурна или Юпитера нет данных по дому — нет смысла анализировать
        return {}

    saturn_sign = transit_positions.get("Сатурн", {}).get("sign")
    jupiter_sign = transit_positions.get("Юпитер", {}).get("sign")

    saturn_aspects = set(aspects_dict.get("Сатурн", []))
    jupiter_aspects = set(aspects_dict.get("Юпитер", []))

    result = {}

    # Пересечения домов аспектирования — двойные аспекты
    double_aspect_houses = saturn_aspects.intersection(jupiter_aspects)
    for house in double_aspect_houses:
        result.setdefault(house, []).append("Двойной аспект: Сатурн и Юпитер аспектируют этот дом")

    # Взаимные аспекты по домам
    if jupiter_house in saturn_aspects:
        result.setdefault(jupiter_house, []).append("Сатурн аспектирует дом Юпитера")

    if saturn_house in jupiter_aspects:
        result.setdefault(saturn_house, []).append("Юпитер аспектирует дом Сатурна")

    # Если обе планеты находятся в одном доме
    if saturn_house == jupiter_house:
        result.setdefault(saturn_house, []).append("Сатурн и Юпитер находятся в одном доме")

    # Если обе планеты в одном знаке
    if saturn_sign == jupiter_sign and saturn_sign is not None:
        result.setdefault("same_sign", []).append("Сатурн и Юпитер находятся в одном знаке")

    return result

def check_sade_sati(transit_positions, natal_positions):
    natal_moon = natal_positions.get('Луна')
    saturn = transit_positions.get('Сатурн')

    if not natal_moon or not saturn:
        return "=== ОТЧЁТ ПО САДЕ САТИ ===\nДанные о Луне или Сатурне отсутствуют."

    natal_house = natal_moon.get('house')
    saturn_house = saturn.get('house')

    if natal_house is None or saturn_house is None:
        return "=== ОТЧЁТ ПО САДЕ САТИ ===\nНет информации о домах Луны или Сатурна."

    diff = abs(saturn_house - natal_house)
    diff = diff if diff <= 6 else 12 - diff

    moon_deg = natal_moon.get('degree', '?')
    moon_sign = natal_moon.get('sign', '?')
    saturn_deg = saturn.get('degree', '?')
    saturn_sign = saturn.get('sign', '?')

    output = [f"=== ОТЧЁТ ПО САДЕ САТИ ===",
              f"Натальная Луна: {moon_deg} в знаке {moon_sign}, дом {natal_house}",
              f"Транзитный Сатурн: {saturn_deg} в знаке {saturn_sign}, дом {saturn_house}",
              f"Разница домов: {diff}"]

    if diff <= 1:
        output.append("⚠️ Саде Сати активна — период испытаний, очищения и глубоких перемен.")
    else:
        output.append("Саде Сати не активна на данный момент.")

    return "\n".join(output)



def get_aspected_houses(planet_name, current_house):
    """
    Возвращает список домов, которые аспектирует планета согласно DRISHTI_MAP.
    Отсчёт аспектируемых домов ведётся с текущего дома, как в Джйотиш.
    """
    offsets = DRISHTI_MAP.get(planet_name, [7])  # По умолчанию — 7-й дом (оппозиция)
    return [((current_house + offset - 2) % 12) + 1 for offset in offsets]


def analyze_each_house(
    rulers_status,
    planets_scores,
    aspects_scores,
    double_aspects_scores,
    aspects_by_house,
    transit_aspecting_houses
):
    """
    Анализ каждого дома с выводом баллов по отдельным категориям и итоговым.
    """
    analysis = {}

    for house in range(1, 13):
        score_ruler = 0
        score_planets = 0
        score_aspects = 0
        score_double_aspects = 0

        reasons = []

        # Управитель дома
        ruler_data = rulers_status.get(house)
        if ruler_data:
            score_ruler = ruler_data.get("score", 0)
            reasons.append(f"Управитель: {score_ruler} баллов — {ruler_data.get('reason', '')}")

        # Планеты в доме (транзитные)
        planets_in_house = planets_scores.get(house, {})
        for planet, data in planets_in_house.items():
            score_planets += data.get("score", 0)
            reasons.append(f"{planet}: {data.get('score', 0)} баллов — {data.get('reason', '')}")

        # Аспекты от транзитных планет — словарь {планета: {"score": int, "reason": str}}
        house_aspects = aspects_scores.get(house, {})
        for planet, aspect_data in house_aspects.items():
            s = aspect_data.get("score", 0)
            score_aspects += s
            reasons.append(aspect_data.get("reason", f"Аспект от {planet}: {s}"))

        # Двойные аспекты
        for asp in double_aspects_scores.get(house, []):
            s = asp.get("score", 0)
            score_double_aspects += s
            reasons.append(f"Двойные аспекты: {s} баллов — {asp.get('reason', '')}")

        # Аспекты дришти (описания)
        if aspects_by_house.get(house):
            reasons.append("Аспекты дришти от транзитных планет:")
            reasons.extend(aspects_by_house[house])

        # Планеты, аспектирующие дом целиком
        planets_aspecting = transit_aspecting_houses.get(house, [])
        if planets_aspecting:
            unique_planets = sorted(set(planets_aspecting))
            reasons.append(f"Аспектируют транзитные планеты: {', '.join(unique_planets)}")

        total_score = score_ruler + score_planets + score_aspects + score_double_aspects

        # Добавим строку с итоговым счётом для удобства
        reasons.append(f"Итоговый балл по дому: {total_score}")

        analysis[house] = {
            "total_score": total_score,
            "score_ruler": score_ruler,
            "score_planets": score_planets,
            "score_aspects": score_aspects,
            "score_double_aspects": score_double_aspects,
            "reasons": reasons or ["Нет значимых факторов"]
        }

    return analysis

def generate_report(houses_analysis):
    """
    Формирует текстовый отчёт по анализу домов с расшифровкой значений домов.
    """
    result = []
    for h in range(1, 13):
        info = houses_analysis.get(h, {})
        meaning = HOUSE_MEANINGS.get(h, "Описание дома отсутствует")
        result.append(
            f"\n=== Дом {h} === ({meaning})\n"
            f"Итог: {info.get('total_score', 0)}\nПричины: \n- " +
            "\n- ".join(info.get("reasons", []))
        )
    return "\n".join(result)


def evaluate_house_ruler(ruler, planet_house_map, transit_positions):
    reason_parts = []
    score_by_house = 0
    score_by_sign = 0
    score_by_motion = 0
    score_by_connections = 0

    ruler_data = transit_positions.get(ruler, {})
    ruler_transit_house = ruler_data.get("house")
    ruler_sign = ruler_data.get("sign")

    # Оценка положения управителя по дому (дустхана, трикона, нейтральный)
    if ruler_transit_house is not None:
        if ruler_transit_house in dusthana_houses:
            reason_parts.append(f"Управитель в транзите в дустхане {ruler_transit_house} (-1 балл)")
            score_by_house = -1
        elif ruler_transit_house in trikon_houses:
            reason_parts.append(f"Управитель в триконе {ruler_transit_house} (+1 балл)")
            score_by_house = 1
        else:
            reason_parts.append(f"Управитель в нейтральном транзитном доме {ruler_transit_house} (0 баллов)")
            score_by_house = 0.5
    else:
        reason_parts.append("Нет данных о доме управителя в транзите")

    # Оценка знака управителя (дружелюбный, враждебный, нейтральный)
    if ruler_sign:
        if ruler_sign in friendly_signs_map.get(ruler, []):
            score_by_sign = 1
            reason_parts.append(f"Управитель в благоприятном знаке {ruler_sign} (+1 балл)")
        elif ruler_sign in enemy_signs_map.get(ruler, []):
            score_by_sign = -1
            reason_parts.append(f"Управитель в неблагоприятном знаке {ruler_sign} (-1 балл)")
        else:
            reason_parts.append(f"Управитель в нейтральном знаке {ruler_sign} (0 баллов)")

    # Оценка движения (ретроградность или прямое движение)
    retrograde = ruler_data.get("retrograde", False)
    if retrograde:
        score_by_motion = -1
        reason_parts.append("Управитель ретрограден (-1 балл)")
    else:
        score_by_motion = 1
        reason_parts.append("Управитель движется прямым ходом (+1 балл)")

    # Проверка соединений и аспектов других планет
    for planet in (malefic_planets | benefic_planets):
        if planet == ruler:
            continue

        planet_data = transit_positions.get(planet)
        if not planet_data:
            continue
        planet_house = planet_data.get("house")
        if planet_house is None or ruler_transit_house is None:
            continue

        # Соединение — планеты в одном доме
        if planet_house == ruler_transit_house:
            if planet in malefic_planets:
                score_by_connections -= 1
                reason_parts.append(f"Управитель в соединении с вредной планетой {planet} (дом {planet_house}) (-1 балл)")
            elif planet in benefic_planets:
                score_by_connections += 1
                reason_parts.append(f"Управитель в соединении с благоприятной планетой {planet} (дом {planet_house}) (+1 балл)")
            else:
                reason_parts.append(f"Управитель в соединении с планетой {planet} (дом {planet_house}) (0 баллов)")

        # Аспект — дом управителя под аспектом планеты
        else:
            drishti_offsets = DRISHTI_MAP.get(planet, [7])  # по умолчанию аспект на 7 дом
            # Вычисляем аспекты планеты — дома, куда она смотрит
            aspected_houses = [((planet_house + offset - 2) % 12) + 1 for offset in drishti_offsets]
            if ruler_transit_house in aspected_houses:
                if planet in malefic_planets:
                    score_by_connections -= 1
                    reason_parts.append(f"Управитель под аспектом вредной планеты {planet} (дом {planet_house}) (-1 балл)")
                elif planet in benefic_planets:
                    score_by_connections += 1
                    reason_parts.append(f"Управитель под аспектом благоприятной планеты {planet} (дом {planet_house}) (+1 балл)")
                else:
                    reason_parts.append(f"Управитель под аспектом планеты {planet} (дом {planet_house}) (0 баллов)")

    total_score = score_by_house + score_by_sign + score_by_motion + score_by_connections

    if total_score == 1:
        reason_parts.append("Управитель дома в хорошем положении")

    reason_parts.append(
        f"Итог: {total_score} (дом: {score_by_house}, знак: {score_by_sign}, движение: {score_by_motion}, связи: {score_by_connections})"
    )

    reason_text = "\n  - ".join(reason_parts)
    return {"score": total_score, "reason": "Причины:\n  - " + reason_text}



def analyze_transits_full(natal_positions, transit_positions):
    """
    Основная функция для анализа транзитов.
    Возвращает текстовый отчёт и подробный словарь с анализом домов.
    """

    # Определение управителей домов
    house_rulers = get_house_rulers(natal_positions, transit_positions)
    house_rulers_map = {house: ruler for house, (ruler, _) in house_rulers.items()}
    planet_house_map = {p: d["house"] for p, d in natal_positions.items()}

    # Оценка управителей домов
    rulers_status = {}
    for house_num, (ruler, transit_house) in house_rulers.items():
        if not ruler:
            continue
        rulers_status[house_num] = evaluate_house_ruler(ruler, planet_house_map, transit_positions)

    # Оценка планет в домах
    planets_scores = {}
    for planet, data in transit_positions.items():
        h = data.get("house")
        if h is None:
            continue
        reason = evaluate_planet_in_house(planet, h)
        score = 1 if "благоприятная" in reason else -1 if "вредная" in reason else 0
        planets_scores.setdefault(h, {})[planet] = {"score": score, "reason": reason}

    # Анализ аспектов транзитных планет
    aspects = transit_aspect_analysis(transit_positions, natal_positions)

    # Получение баллов по аспектам, исключая аспекты управителя на свой дом
    aspect_scores_raw = evaluate_house_aspects({
        planet: data["house"]
        for planet, data in transit_positions.items()
        if data.get("house") is not None
    }, house_rulers_map)

    # Преобразуем в формат {дом: [{score: int, reason: str}, ...]}
    aspects_score_dict = {
        house: {
            planet: {
                "score": score,
                "reason": f"Аспект от {planet}: {score} балл{'ов' if abs(score) != 1 else ''} — {'позитивный' if score > 0 else 'негативный' if score < 0 else 'нейтральный'}"
            }
            for planet, score in planet_scores.items()
        }
        for house, planet_scores in aspect_scores_raw.items() if planet_scores
    }
    # Анализ двойных аспектов Сатурна и Юпитера
    double_aspects = analyze_double_aspects_from_aspects(transit_positions, aspects)
    double_aspects_score_dict = {
        h: [{"score": 0, "reason": "Двойной аспект Юпитера и Сатурна"}]
        for h, v in double_aspects.items() if v and "Двойной аспект" in " ".join(v)
    }

    # Развернутые аспекты по домам
    aspects_by_house = group_aspects_by_house(aspects)

    # Планеты, аспектирующие дома целиком
    transit_aspecting_houses = get_transit_planets_aspecting_houses(transit_positions)

    # Итоговый анализ
    houses_analysis = analyze_each_house(
        rulers_status,
        planets_scores,
        aspects_score_dict,
        double_aspects_score_dict,
        aspects_by_house,
        transit_aspecting_houses
    )

    report = generate_report(houses_analysis)
    return report, houses_analysis

def get_house_rulers(natal_positions, transit_positions):
    """
    Возвращает словарь: дом -> (управитель дома по знаку, дом транзитного положения управителя).
    Исходит из знака Лагны и порядка знаков.
    """
    lagna_data = natal_positions.get("Лагна")
    if not lagna_data:
        return {}

    lagna_sign = lagna_data.get("sign")
    if not lagna_sign:
        return {}

    zodiac_order = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]

    try:
        start_idx = zodiac_order.index(lagna_sign)
    except ValueError:
        return {}

    result = {}
    for i in range(12):
        house_num = i + 1
        sign_idx = (start_idx + i) % 12
        sign = zodiac_order[sign_idx]
        ruler = SIGN_RULERS.get(sign)

        transit_house = "-"
        if ruler and ruler in transit_positions:
            transit_house = transit_positions[ruler].get("house", "-")

        result[house_num] = (ruler, transit_house)

    return result



def degree_str_to_float(degree_str: str) -> float:
    """
    Преобразует строку с градусами в число с дробной частью.
    Формат входа: "dd°mm'ss''"
    """
    try:
        parts = degree_str.replace("''", "").split("°")
        deg = float(parts[0])
        minutes, seconds = parts[1].split("'")
        minutes = float(minutes)
        seconds = float(seconds)
        return deg + minutes / 60 + seconds / 3600
    except Exception as e:
        print(f"[ОШИБКА] Неверное значение градуса: '{degree_str}': {e}")
        return 0.0


# --------- НОВАЯ ФУНКЦИЯ ДЛЯ ПОДРОБНОГО АНАЛИЗА ТРАНЗИТНЫХ ПЛАНЕТ ---------

def analyze_transit_planets_detailed(transit_positions):
    """
    Возвращает подробный разбор каждой транзитной планеты:
    - текущий дом
    - аспектируемые дома (дришти)
    - ретроградность
    - оценка качества планеты по положению в доме
    Это полезно для отладки и глубокого анализа транзитов.
    """
    analysis = {}
    for planet, data in transit_positions.items():
        house = data.get("house")
        if house is None:
            continue

        retrograde = data.get("retrograde", False)
        drishti_houses = calculate_drishti(planet, house)
        quality = evaluate_planet_in_house(planet, house)

        analysis[planet] = {
            "текущий_дом": house,
            "ретроградность": retrograde,
            "аспектируемые_дома": drishti_houses,
            "оценка_по_дому": quality,
        }

    return analysis

def format_transit_planets_detailed(analysis_dict):
    """
    Форматирует подробный анализ транзитных планет в удобочитаемый текст.
    """
    lines = []
    for planet, info in analysis_dict.items():
        retro = "ретроградна" if info["ретроградность"] else "прямое движение"
        aspects = ", ".join(str(h) for h in info["аспектируемые_дома"])
        lines.append(
            f"{planet}: сейчас в доме {info['текущий_дом']} ({retro}); "
            f"аспектирует дома: {aspects}; "
            f"оценка влияния: {info['оценка_по_дому']}"
        )
    return "\n".join(lines)

