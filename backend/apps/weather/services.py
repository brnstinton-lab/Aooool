import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Осаждающий туман",
    51: "Слабая морось",
    53: "Умеренная морось",
    55: "Плотная морось",
    56: "Слабая ледяная морось",
    57: "Плотная ледяная морось",
    61: "Небольшой дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Слабый ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Небольшой снегопад",
    73: "Умеренный снегопад",
    75: "Сильный снегопад",
    77: "Снежные зёрна",
    80: "Слабый ливневый дождь",
    81: "Умеренный ливневый дождь",
    82: "Сильный ливневый дождь",
    85: "Слабый снегопад",
    86: "Сильный снегопад",
    95: "Гроза",
    96: "Гроза со слабым градом",
    99: "Гроза с сильным градом",
}

WMO_WEATHER_ICONS: Dict[int, str] = {
    0: "wb_sunny",
    1: "partly_cloudy_day",
    2: "partly_cloudy_day",
    3: "cloud",
    45: "foggy",
    48: "foggy",
    51: "rainy",
    53: "rainy",
    55: "rainy",
    56: "weather_snowy",
    57: "weather_snowy",
    61: "rainy",
    63: "rainy",
    65: "rainy_heavy",
    66: "weather_snowy",
    67: "weather_snowy",
    71: "weather_snowy",
    73: "weather_snowy",
    75: "snowing",
    77: "snowing",
    80: "rainy",
    81: "rainy",
    82: "rainy_heavy",
    85: "weather_snowy",
    86: "snowing",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


def get_weather_description(code: Optional[int]) -> str:
    """Возвращает текстовое описание погоды на русском языке по WMO коду."""
    if code is None:
        return "Неизвестно"
    return WMO_WEATHER_CODES.get(int(code), "Переменная облачность")


def get_weather_icon(code: Optional[int]) -> str:
    """Возвращает название Material Symbol иконки для UI."""
    if code is None:
        return "partly_cloudy_day"
    return WMO_WEATHER_ICONS.get(int(code), "partly_cloudy_day")


def fetch_open_meteo_data(latitude: float, longitude: float, timeout_seconds: int = 5) -> Dict[str, Any]:
    """
    Выполняет HTTP-запрос к Open-Meteo API и возвращает сырые данные JSON.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunrise,sunset"
        f"&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&timezone=auto&forecast_days=7"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AUL-Village-SuperApp/1.0", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        if response.status != 200:
            raise urllib.error.HTTPError(
                url, response.status, f"Open-Meteo HTTP status {response.status}", response.headers, None
            )
        raw_body = response.read().decode("utf-8")
        return json.loads(raw_body)


def normalize_weather_data(raw_data: Dict[str, Any], location_name: str, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Нормализует сырой ответ Open-Meteo в чистую структуру с числовыми типами.
    """
    current_raw = raw_data.get("current", {})
    daily_raw = raw_data.get("daily", {})

    weather_code = int(current_raw.get("weather_code", 0)) if current_raw.get("weather_code") is not None else 0
    description = get_weather_description(weather_code)

    # Первые sunrise / sunset из daily
    daily_sunrises = daily_raw.get("sunrise", [])
    daily_sunsets = daily_raw.get("sunset", [])
    sunrise_str = daily_sunrises[0] if daily_sunrises else ""
    sunset_str = daily_sunsets[0] if daily_sunsets else ""

    # Формируем прогноз по дням
    forecast_list = []
    dates = daily_raw.get("time", [])
    weather_codes = daily_raw.get("weather_code", [])
    temps_max = daily_raw.get("temperature_2m_max", [])
    temps_min = daily_raw.get("temperature_2m_min", [])
    precipitations = daily_raw.get("precipitation_sum", [])
    wind_speeds = daily_raw.get("wind_speed_10m_max", [])

    for i in range(len(dates)):
        day_code = int(weather_codes[i]) if i < len(weather_codes) and weather_codes[i] is not None else 0
        forecast_list.append({
            "date": dates[i],
            "weather_code": day_code,
            "description": get_weather_description(day_code),
            "temp_max": float(temps_max[i]) if i < len(temps_max) and temps_max[i] is not None else 0.0,
            "temp_min": float(temps_min[i]) if i < len(temps_min) and temps_min[i] is not None else 0.0,
            "precipitation": float(precipitations[i]) if i < len(precipitations) and precipitations[i] is not None else 0.0,
            "wind_speed_max": float(wind_speeds[i]) if i < len(wind_speeds) and wind_speeds[i] is not None else 0.0,
            "sunrise": daily_sunrises[i] if i < len(daily_sunrises) else "",
            "sunset": daily_sunsets[i] if i < len(daily_sunsets) else "",
        })

    return {
        "location": {
            "name": location_name,
            "latitude": float(latitude),
            "longitude": float(longitude),
        },
        "current": {
            "temperature": float(current_raw.get("temperature_2m", 0.0)),
            "apparent_temperature": float(current_raw.get("apparent_temperature", 0.0)),
            "humidity": int(current_raw.get("relative_humidity_2m", 0)),
            "precipitation": float(current_raw.get("precipitation", 0.0)),
            "wind_speed": float(current_raw.get("wind_speed_10m", 0.0)),
            "wind_direction": int(current_raw.get("wind_direction_10m", 0)),
            "weather_code": weather_code,
            "description": description,
        },
        "sun": {
            "sunrise": sunrise_str,
            "sunset": sunset_str,
        },
        "forecast": forecast_list,
    }


def get_weather(latitude: Optional[float] = None, longitude: Optional[float] = None, location_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Основная сервисная функция для получения данных о погоде.
    - Берет координаты из Django settings, если не переданы явно.
    - Проверяет кэш Django (10 минут).
    - При сбое внешнего API возвращает последнее кэшированное значение (stale cache) или безопасный fallback.
    - Никогда не выбрасывает необработанный traceback наружу.
    """
    lat = float(latitude if latitude is not None else getattr(settings, "WEATHER_LATITUDE", 45.8344))
    lon = float(longitude if longitude is not None else getattr(settings, "WEATHER_LONGITUDE", 80.6067))
    loc_name = str(location_name if location_name is not None else getattr(settings, "WEATHER_LOCATION_NAME", "Кабанбай"))
    cache_ttl = int(getattr(settings, "WEATHER_CACHE_TIMEOUT", 600))

    cache_key = f"weather_data_{lat:.4f}_{lon:.4f}"
    stale_cache_key = f"weather_stale_data_{lat:.4f}_{lon:.4f}"

    # 1. Проверяем свежий кэш
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # 2. Пытаемся запросить данные с Open-Meteo
    try:
        raw_data = fetch_open_meteo_data(lat, lon)
        normalized_data = normalize_weather_data(raw_data, loc_name, lat, lon)
        
        # Сохраняем в кэш
        cache.set(cache_key, normalized_data, timeout=cache_ttl)
        cache.set(stale_cache_key, normalized_data, timeout=86400)  # Резервный кэш на сутки
        return normalized_data
    except Exception as exc:
        logger.warning("Ошибка при получении погоды от Open-Meteo: %s", exc)

        # 3. Fallback: пробуем резервный кэш
        stale_data = cache.get(stale_cache_key)
        if stale_data is not None:
            return stale_data

        # 4. Безопасный дефолтный ответ в случае полной недоступности
        return {
            "location": {
                "name": loc_name,
                "latitude": lat,
                "longitude": lon,
            },
            "current": {
                "temperature": 18.0,
                "apparent_temperature": 17.0,
                "humidity": 50,
                "precipitation": 0.0,
                "wind_speed": 5.0,
                "wind_direction": 0,
                "weather_code": 1,
                "description": "Переменная облачность",
            },
            "sun": {
                "sunrise": "",
                "sunset": "",
            },
            "forecast": [],
            "_error": "Данные о погоде временно недоступны",
        }
