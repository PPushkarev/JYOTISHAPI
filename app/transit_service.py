# transit_service.py
from datetime import datetime
from core import calculate_julian_day
from core_files.transit_analys import (
    calculate_transit_positions,
    analyze_transits_full,
    check_sade_sati,
    get_house_rulers,
    analyze_transit_planets_detailed,
    transit_aspect_analysis,
    analyze_double_aspects_from_aspects
)
from core_files.vimshottari import get_vimshottari_dasha_states

def get_transit_analysis_payload(chart_data: dict, date_str: str) -> dict:
    """
    Generates a full JSON payload with transit analysis based on the natal chart.
    Includes:
      - Transit planetary positions
      - House scores
      - House rulers
      - Planetary aspects
      - Detailed house and planet analysis
      - Sade Sati check
      - Vimshottari Dasha state
    """

    def get_house_status(score: float) -> str:
        """Helper to assign human-readable status based on numerical score."""
        if score >= 3:
            return "Очень благоприятно"
        elif score >= 1:
            return "Благоприятно"
        elif score > -1:
            return "Нейтрально"
        elif score > -3:
            return "Неблагоприятно"
        else:
            return "Критически неблагоприятно"

    # ------------------------------------------------------------------
    # 1. Natal Data Extraction
    # ------------------------------------------------------------------
    natal_planets = chart_data.get("planets", {})
    lagna_deg = chart_data.get("lagna")
    lat = chart_data.get("latitude")
    lon = chart_data.get("longitude")
    jd_birth = chart_data.get("julian_day")

    # ------------------------------------------------------------------
    # 2. Transit Date Handling
    # ------------------------------------------------------------------
    dt_transit = datetime.strptime(date_str, "%Y-%m-%d")
    jd_transit = calculate_julian_day(dt_transit, 0.0)

    # ------------------------------------------------------------------
    # 3. Calculate Transit Positions
    # ------------------------------------------------------------------
    transit_positions = calculate_transit_positions(jd_transit, lagna_deg, lat, lon)

    # ------------------------------------------------------------------
    # 4. House Analysis (Scores and Conclusions)
    # ------------------------------------------------------------------
    raw_report, houses_scores = analyze_transits_full(natal_planets, transit_positions)

    # Apply readable statuses once houses_scores dictionary is generated
    for house_id in houses_scores:
        score = houses_scores[house_id].get("total_score", 0)
        houses_scores[house_id]["status"] = get_house_status(score)

    # ------------------------------------------------------------------
    # 5. Aspect Analysis
    # ------------------------------------------------------------------
    single_aspects = transit_aspect_analysis(transit_positions, natal_planets)
    double_aspects = analyze_double_aspects_from_aspects(transit_positions, single_aspects)

    # ------------------------------------------------------------------
    # 6. House Rulers Analysis
    # ------------------------------------------------------------------
    house_rulers = get_house_rulers(natal_planets, transit_positions)

    # ------------------------------------------------------------------
    # 7. Detailed Planet and House Insights
    # ------------------------------------------------------------------
    planets_detailed = analyze_transit_planets_detailed(transit_positions)

    # ------------------------------------------------------------------
    # 8. Sade Sati Calculation
    # ------------------------------------------------------------------
    sade_sati_data = check_sade_sati(transit_positions, natal_planets)

    # ------------------------------------------------------------------
    # 9. Vimshottari Dasha Periods
    # ------------------------------------------------------------------
    dashas = None
    moon_data = natal_planets.get("Луна")
    if jd_birth and moon_data:
        dashas = get_vimshottari_dasha_states(jd_transit, jd_birth, moon_data)

    # ------------------------------------------------------------------
    # 10. Final Payload Construction
    # ------------------------------------------------------------------
    payload = {
        "meta": {
            "engine": "AstroMind",
            "engine_version": "2.0.0",
            "calculation_timestamp": datetime.utcnow().isoformat(),
            "transit_date": date_str,
            "sidereal_ayanamsa": "Lahiri"
        },
        "natal_chart": {
            "lagna": lagna_deg,
            "planets": natal_planets,
            "coordinates": {"latitude": lat, "longitude": lon},
            "julian_day": jd_birth
        },
        "transits": {
            "positions": transit_positions
        },
        "derived_tables": {
            "houses": {
                "scores": houses_scores  # Dict with houses and their calculated scores
            },
            "house_rulers": house_rulers,  # Dict with house ruling planets
            "aspects": {
                "single": single_aspects,
                "double": double_aspects
            },
            "planets_detailed": planets_detailed,
            "special_conditions": {
                "sade_sati": sade_sati_data
            },
            "periods": {
                "vimshottari": dashas
            }
        },
        "raw_logs": {
            "engine_report": raw_report
        }
    }

    return payload