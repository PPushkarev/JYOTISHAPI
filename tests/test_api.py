import pytest
from fastapi.testclient import TestClient
from app.api import app  # Importing your FastAPI application object
import json
import time

# Initialize the TestClient
# This allows making API requests "in-memory" without running uvicorn
client = TestClient(app)

# Your test data (structure remains unchanged)
test_chart_data = {
    "name": "Кошка",
    "date": "1988-02-02",
    "time": "02:02",
    "city": "Москва",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "utc_offset": 3.0,
    "julian_day": 2447193.45972,
    "lagna": 198.97,
    "sign": "Весы",
    "planets": {
        "Лагна": {"degree": "18°58'5''", "sign": "Весы", "house": 1, "nakshatra": "Свати", "pada": 4,
                  "nakshatra_lord": "Раху", "retrograde": False, "display_name": "Лагна"},
        "Солнце": {"degree": "18°37'6''", "sign": "Козерог", "house": 4, "nakshatra": "Шравана", "pada": 3,
                   "nakshatra_lord": "Луна", "retrograde": False, "display_name": "Солнце"},
        "Луна": {"degree": "8°45'15''", "sign": "Рак", "house": 10, "nakshatra": "Пушья", "pada": 2,
                 "nakshatra_lord": "Сатурн", "retrograde": False, "display_name": "Луна",
                 "longitude": 8.754166666666666},
        "Марс": {"degree": "22°33'1''", "sign": "Скорпион", "house": 2, "nakshatra": "Джйештха", "pada": 2,
                 "nakshatra_lord": "Меркурий", "retrograde": False, "display_name": "Марс"},
        "Меркурий": {"degree": "4°22'1''", "sign": "Водолей", "house": 5, "nakshatra": "Дхаништха", "pada": 4,
                     "nakshatra_lord": "Марс", "retrograde": False, "display_name": "Меркурий"},
        "Юпитер": {"degree": "29°51'56''", "sign": "Рыбы", "house": 6, "nakshatra": "Ревати", "pada": 4,
                   "nakshatra_lord": "Меркурий", "retrograde": False, "display_name": "Юпитер"},
        "Венера": {"degree": "27°15'17''", "sign": "Водолей", "house": 5, "nakshatra": "Пурва-Бхадрапада", "pada": 3,
                   "nakshatra_lord": "Юпитер", "retrograde": False, "display_name": "Венера"},
        "Сатурн": {"degree": "5°13'12''", "sign": "Стрелец", "house": 3, "nakshatra": "Мула", "pada": 2,
                   "nakshatra_lord": "Кету", "retrograde": False, "display_name": "Сатурн"},
        "Раху": {"degree": "1°47'7''", "sign": "Рыбы", "house": 6, "nakshatra": "Пурва-Бхадрапада", "pada": 4,
                 "nakshatra_lord": "Юпитер", "retrograde": True, "display_name": "Раху R"},
        "Кету": {"degree": "1°47'7''", "sign": "Дева", "house": 12, "nakshatra": "Уттара-Пхалгуни", "pada": 2,
                 "nakshatra_lord": "Солнце", "retrograde": True, "display_name": "Кету R"}
    }
}

TRANSIT_DATE = "2025-12-29"


def test_transit_api_contract():
    """Verify API response structure (Contract Testing)"""
    payload = {
        "chart_data": test_chart_data,
        "transit_date": TRANSIT_DATE
    }

    # Make request via the internal TestClient
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 200
    result = response.json()

    # Verify key blocks (META, Natal, Transits)
    assert "meta" in result
    assert result["meta"]["transit_date"] == TRANSIT_DATE
    assert "natal_chart" in result
    assert "transits" in result
    assert "derived_tables" in result

    # Verify house calculations
    houses = result["derived_tables"].get("houses", {}).get("scores", {})
    assert "5" in houses
    print(f"\n✅ Contract valid. House 5 score: {houses['5'].get('total_score')}")


def test_invalid_date_format():
    """Test protection against incorrect date format (should return 422)"""
    bad_payload = {
        "chart_data": test_chart_data,
        "transit_date": "not-a-date"
    }
    response = client.post("/api/v1/analyze", json=bad_payload)
    assert response.status_code == 422
    print("\n✅ API correctly rejected invalid date.")


def test_missing_required_fields():
    """Test protection against incomplete requests"""
    response = client.post("/api/v1/analyze", json={"unknown_field": "test"})
    assert response.status_code == 422
    print("\n✅ API correctly rejected incomplete request.")


@pytest.mark.performance
def test_performance_benchmark():
    """Performance measurement (at least 10 iterations)"""
    payload = {"chart_data": test_chart_data, "transit_date": TRANSIT_DATE}

    times = []
    for _ in range(10):
        start = time.time()
        client.post("/api/v1/analyze", json=payload)
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    print(f"\n✅ Average time (TestClient): {avg_time:.4f} sec.")
    assert avg_time < 0.2  # Should be fast within memory limits