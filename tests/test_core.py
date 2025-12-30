import pytest
from datetime import datetime
# Importing functions directly from your core engine
# (Assuming the main core file is named core.py)
from core import degree_str_to_float, get_zodiac_sign, get_nakshatra_and_pada_by_degree, calculate_julian_day

# --- String Parsing Tests ---

def test_degree_str_to_float_valid():
    """Verify conversion of a coordinate string (e.g., '18°58'5''') to a decimal float."""
    input_str = "18°58'5''"
    expected = 18 + 58/60 + 5/3600
    assert degree_str_to_float(input_str) == pytest.approx(expected, rel=1e-7)

def test_degree_str_to_float_zero():
    """Verify error handling for empty or malformed degree strings."""
    assert degree_str_to_float("invalid") == 0.0

# --- Zodiac Logic Tests (360° Circle Mathematics) ---

@pytest.mark.parametrize("degree, expected_sign", [
    (15.0, "Овен"),      # 0-30: Aries
    (45.0, "Телец"),     # 30-60: Taurus
    (198.97, "Весы"),    # Example from your calculation log: Libra
    (345.0, "Рыбы"),     # 330-360: Pisces
])
def test_get_zodiac_sign(degree, expected_sign):
    """Verify correct Zodiac sign identification based on planetary degree."""
    assert get_zodiac_sign(degree) == expected_sign

# --- Lunar Logic Tests (Nakshatras and Padas) ---



def test_get_nakshatra_and_pada_logic():
    """Verify Nakshatra and Pada calculation for specific degrees."""
    # 0 degrees is the beginning of Ashwini, 1st Pada
    nak, pada = get_nakshatra_and_pada_by_degree(0.0)
    assert nak == "Ашвини"
    assert pada == 1

    # 13.333... degrees is the start of Bharani (the second Nakshatra)
    nak, pada = get_nakshatra_and_pada_by_degree(13.4)
    assert nak == "Бхарани"
    assert pada == 1

# --- Julian Day Calculation Tests (Astronomical Accuracy) ---



def test_julian_day_consistency():
    """Verify that the same datetime input consistently produces the same Julian Day (JD)."""
    dt = datetime(2000, 1, 1, 12, 0)
    jd1 = calculate_julian_day(dt, 0.0)
    jd2 = calculate_julian_day(dt, 0.0)
    assert jd1 == jd2
    assert isinstance(jd1, float)