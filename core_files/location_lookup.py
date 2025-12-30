
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import datetime

def get_location_data(city_name: str, birth_dt: datetime):
    geolocator = Nominatim(user_agent="astro_locator")
    location = geolocator.geocode(city_name)

    if not location:
        raise ValueError("Город не найден.")

    latitude = location.latitude
    longitude = location.longitude

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)

    if not timezone_str:
        raise ValueError("Не удалось определить часовой пояс.")

    tz = ZoneInfo(timezone_str)
    localized_dt = birth_dt.replace(tzinfo=tz)
    utc_offset = localized_dt.utcoffset().total_seconds() / 3600

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_str,
        "utc_offset": utc_offset,
        "localized_dt": localized_dt
    }
