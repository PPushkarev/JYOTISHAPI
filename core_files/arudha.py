from core_files.constants import SIGN_RULERS, ZODIAC_SIGNS, NAKSHATRA_LENGTH, NAKSHATRAS


def degree_str_to_float(degree_str: str) -> float:
    try:
        parts = degree_str.replace("''", "").split("°")
        deg = float(parts[0])
        minutes, seconds = parts[1].split("'")
        return deg + float(minutes) / 60 + float(seconds) / 3600
    except Exception as e:
        print(f"Ошибка при парсинге '{degree_str}': {e}")
        return 0.0


def get_nakshatra_and_pada_by_degree(degree: float):
    total_deg = degree % 360
    nak_index = int(total_deg // NAKSHATRA_LENGTH)
    pada = int((total_deg % NAKSHATRA_LENGTH) // (NAKSHATRA_LENGTH / 4)) + 1
    nak = NAKSHATRAS[nak_index]
    return nak, pada


def calculate_arudha_table(planet_data, lagna_sign_index):
    arudha_table = []

    planet_houses = {p: d["house"] for p, d in planet_data.items()}
    planet_degrees = {}
    planet_signs = {}

    for planet, data in planet_data.items():
        deg_str = data.get("degree")
        if isinstance(deg_str, str):
            deg = degree_str_to_float(deg_str)
        else:
            deg = deg_str
        planet_degrees[planet] = deg
        planet_signs[planet] = data.get("sign")

    for house in range(1, 13):
        house_sign_index = (lagna_sign_index + house - 1) % 12
        house_sign = ZODIAC_SIGNS[house_sign_index]
        ruler = SIGN_RULERS.get(house_sign)

        ruler_house = planet_houses.get(ruler)
        ruler_deg = planet_degrees.get(ruler)
        ruler_sign = planet_signs.get(ruler)

        if ruler is None or ruler_house is None or ruler_deg is None or ruler_sign is None:
            continue

        distance = (ruler_house - house) % 12
        arudha_house = (ruler_house + distance) % 12 or 12

        if arudha_house == house or arudha_house == ((house + 6 - 1) % 12) + 1:
            arudha_house = (house + 10) % 12 or 12

        arudha_sign_index = (lagna_sign_index + arudha_house - 1) % 12
        arudha_sign = ZODIAC_SIGNS[arudha_sign_index]

        ruler_sign_index = ZODIAC_SIGNS.index(ruler_sign)
        deg_in_sign = ruler_deg - (ruler_sign_index * 30)
        if deg_in_sign < 0:
            deg_in_sign += 30

        arudha_absolute_degree = (arudha_sign_index * 30) + deg_in_sign
        nak, pada = get_nakshatra_and_pada_by_degree(arudha_absolute_degree)

        arudha_table.append({
            "Дом": house,
            "Метка": "AL" if house == 1 else f"A{house}",
            "Знак Арудхи": arudha_sign,
            "Градусы": round(arudha_absolute_degree, 2),
            "Накшатра": nak,
            "Пада": pada
        })

    # === Upapada Lagna (UL) ===
    twelfth_house = 12
    twelfth_sign_index = (lagna_sign_index + twelfth_house - 1) % 12
    twelfth_sign = ZODIAC_SIGNS[twelfth_sign_index]
    ruler = SIGN_RULERS.get(twelfth_sign)

    if ruler:
        ruler_house = planet_houses.get(ruler)
        ruler_deg = planet_degrees.get(ruler)
        ruler_sign = planet_signs.get(ruler)

        if ruler_house and ruler_deg is not None and ruler_sign:
            distance = (ruler_house - twelfth_house) % 12
            ul_house = (ruler_house + distance) % 12 or 12

            if ul_house == twelfth_house or ul_house == ((twelfth_house + 6 - 1) % 12) + 1:
                ul_house = (twelfth_house + 10) % 12 or 12

            ul_sign_index = (lagna_sign_index + ul_house - 1) % 12
            ul_sign = ZODIAC_SIGNS[ul_sign_index]

            ruler_sign_index = ZODIAC_SIGNS.index(ruler_sign)
            deg_in_sign = ruler_deg - (ruler_sign_index * 30)
            if deg_in_sign < 0:
                deg_in_sign += 30

            ul_absolute_degree = (ul_sign_index * 30) + deg_in_sign
            nak, pada = get_nakshatra_and_pada_by_degree(ul_absolute_degree)

            arudha_table.append({
                "Дом": twelfth_house,
                "Метка": "UL",
                "Знак Арудхи": ul_sign,
                "Градусы": round(ul_absolute_degree, 2),
                "Накшатра": nak,
                "Пада": pada
            })

    return arudha_table



def get_nakshatra_by_longitude(degree: float) -> str:
    index = int(degree // NAKSHATRA_LENGTH) % 27
    return NAKSHATRAS[index]
