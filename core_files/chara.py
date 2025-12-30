# from constants import NAKSHATRAS, CHARA_DASHA_YEARS, nakshatra_lords
#
# def calculate_chara_dasha(lagna_degree: float, start_year: int):
#     """
#     Расчет Чара Даша по ДР Рао
#
#     lagna_degree: градусы Лагны (0-360)
#     start_year: начальный год (например, год рождения)
#
#     Возвращает список даш с:
#     - номер накшатры (1-27)
#     - лорд накшатры (планета)
#     - начало даши (год)
#     # - окончание даши (год)
#     """
#
#     nak_index = int(lagna_degree // (360 / 27))
#     nak_progress = (lagna_degree % (360 / 27)) / (360 / 27)
#     remaining_fraction = 1 - nak_progress
#
#     dasha_list = []
#     current_year = start_year
#
#     for i in range(27):
#         current_nak = (nak_index + i) % 27
#         lord = nakshatra_lords.get(NAKSHATRAS[current_nak], "Unknown")
#
#         if i == 0:
#             duration = CHARA_DASHA_YEARS[current_nak] * remaining_fraction
#         else:
#             duration = CHARA_DASHA_YEARS[current_nak]
#
#         dasha_list.append({
#             "Nakshatra Number": current_nak + 1,
#             "Nakshatra": NAKSHATRAS[current_nak],
#             "Lord": lord,
#             "Start Year": round(current_year, 2),
#             "End Year": round(current_year + duration, 2),
#             "Duration Years": round(duration, 2)
#         })
#
#         current_year += duration
#
#     return dasha_list
