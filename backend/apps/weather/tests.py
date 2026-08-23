import json
from unittest.mock import patch, MagicMock
import urllib.error
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.cache import cache
from apps.weather.services import (
    get_weather,
    get_weather_description,
    get_weather_icon,
    normalize_weather_data,
    WMO_WEATHER_CODES,
)


MOCK_OPEN_METEO_RESPONSE = {
    "latitude": 45.8344,
    "longitude": 80.6067,
    "generationtime_ms": 0.12,
    "utc_offset_seconds": 18000,
    "timezone": "Asia/Almaty",
    "timezone_abbreviation": "+05",
    "elevation": 450.0,
    "current_units": {
        "time": "iso8601",
        "interval": "seconds",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "apparent_temperature": "°C",
        "precipitation": "mm",
        "weather_code": "wmo code",
        "wind_speed_10m": "km/h",
        "wind_direction_10m": "°"
    },
    "current": {
        "time": "2026-08-21T12:00",
        "interval": 900,
        "temperature_2m": 22.4,
        "relative_humidity_2m": 48,
        "apparent_temperature": 21.8,
        "precipitation": 0.0,
        "weather_code": 1,
        "wind_speed_10m": 14.5,
        "wind_direction_10m": 180
    },
    "daily_units": {
        "time": "iso8601",
        "weather_code": "wmo code",
        "temperature_2m_max": "°C",
        "temperature_2m_min": "°C",
        "precipitation_sum": "mm",
        "wind_speed_10m_max": "km/h",
        "sunrise": "iso8601",
        "sunset": "iso8601"
    },
    "daily": {
        "time": ["2026-08-21", "2026-08-22", "2026-08-23", "2026-08-24", "2026-08-25"],
        "weather_code": [1, 0, 61, 2, 0],
        "temperature_2m_max": [25.0, 27.5, 20.0, 24.0, 26.5],
        "temperature_2m_min": [14.0, 15.2, 13.0, 12.5, 14.8],
        "precipitation_sum": [0.0, 0.0, 4.2, 0.2, 0.0],
        "wind_speed_10m_max": [16.0, 12.0, 22.5, 15.0, 10.0],
        "sunrise": [
            "2026-08-21T05:43",
            "2026-08-22T05:44",
            "2026-08-23T05:45",
            "2026-08-24T05:46",
            "2026-08-25T05:47"
        ],
        "sunset": [
            "2026-08-21T19:35",
            "2026-08-22T19:33",
            "2026-08-23T19:31",
            "2026-08-24T19:29",
            "2026-08-25T19:27"
        ]
    }
}


class WeatherServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_wmo_weather_description(self):
        """Проверка перевода WMO кодов погоды на русский"""
        self.assertEqual(get_weather_description(0), "Ясно")
        self.assertEqual(get_weather_description(2), "Переменная облачность")
        self.assertEqual(get_weather_description(61), "Небольшой дождь")
        self.assertEqual(get_weather_description(71), "Небольшой снегопад")
        self.assertEqual(get_weather_description(95), "Гроза")
        self.assertEqual(get_weather_description(999), "Переменная облачность")

    def test_wmo_weather_icons(self):
        """Проверка возврата Material Symbol иконок для погоды"""
        self.assertEqual(get_weather_icon(0), "wb_sunny")
        self.assertEqual(get_weather_icon(61), "rainy")
        self.assertEqual(get_weather_icon(95), "thunderstorm")

    def test_normalize_weather_data(self):
        """Проверка корректной нормализации структуры данных и типов"""
        normalized = normalize_weather_data(
            MOCK_OPEN_METEO_RESPONSE,
            location_name="Кабанбай",
            latitude=45.8344,
            longitude=80.6067
        )

        self.assertEqual(normalized["location"]["name"], "Кабанбай")
        self.assertAlmostEqual(normalized["location"]["latitude"], 45.8344)
        self.assertAlmostEqual(normalized["location"]["longitude"], 80.6067)

        current = normalized["current"]
        self.assertIsInstance(current["temperature"], (int, float))
        self.assertEqual(current["temperature"], 22.4)
        self.assertIsInstance(current["humidity"], int)
        self.assertEqual(current["humidity"], 48)
        self.assertIsInstance(current["wind_speed"], (int, float))
        self.assertEqual(current["wind_speed"], 14.5)
        self.assertIsInstance(current["precipitation"], (int, float))
        self.assertEqual(current["precipitation"], 0.0)
        self.assertEqual(current["weather_code"], 1)
        self.assertEqual(current["description"], "Преимущественно ясно")

        sun = normalized["sun"]
        self.assertEqual(sun["sunrise"], "2026-08-21T05:43")
        self.assertEqual(sun["sunset"], "2026-08-21T19:35")

        forecast = normalized["forecast"]
        self.assertEqual(len(forecast), 5)
        self.assertEqual(forecast[0]["date"], "2026-08-21")
        self.assertEqual(forecast[0]["temp_max"], 25.0)
        self.assertEqual(forecast[0]["temp_min"], 14.0)
        self.assertEqual(forecast[2]["weather_code"], 61)
        self.assertEqual(forecast[2]["description"], "Небольшой дождь")

    @patch("apps.weather.services.fetch_open_meteo_data")
    def test_get_weather_success_and_caching(self, mock_fetch):
        """Проверка успешного запроса и работы кэша"""
        mock_fetch.return_value = MOCK_OPEN_METEO_RESPONSE

        # Первый вызов — делает запрос
        data1 = get_weather(latitude=45.8344, longitude=80.6067, location_name="Кабанбай")
        self.assertEqual(mock_fetch.call_count, 1)
        self.assertEqual(data1["current"]["temperature"], 22.4)

        # Второй вызов — должен взять из кэша Django
        data2 = get_weather(latitude=45.8344, longitude=80.6067, location_name="Кабанбай")
        self.assertEqual(mock_fetch.call_count, 1)  # Не вызывался повторно
        self.assertEqual(data2["current"]["temperature"], 22.4)

    @patch("apps.weather.services.fetch_open_meteo_data")
    def test_get_weather_api_failure_fallback(self, mock_fetch):
        """Проверка обработки ошибок API с возвратом резервного ответа"""
        mock_fetch.side_effect = urllib.error.URLError("Connection timed out")

        # При сбое возвращается безопасная структура без необработанного исключения
        data = get_weather(latitude=45.8344, longitude=80.6067, location_name="Кабанбай")
        self.assertIn("location", data)
        self.assertIn("current", data)
        self.assertIn("_error", data)

    @patch("apps.weather.services.fetch_open_meteo_data")
    def test_get_weather_stale_cache_on_failure(self, mock_fetch):
        """При сбое API возвращается сохранённый резервный кэш (stale cache)"""
        # Сначала успешный запрос
        mock_fetch.return_value = MOCK_OPEN_METEO_RESPONSE
        get_weather(latitude=45.8344, longitude=80.6067, location_name="Кабанбай")

        # Очищаем только свежий кэш, симулируя истечение 10 минут
        cache_key = "weather_data_45.8344_80.6067"
        cache.delete(cache_key)

        # Теперь API падает с ошибкой
        mock_fetch.side_effect = urllib.error.URLError("Service unavailable")
        fallback_data = get_weather(latitude=45.8344, longitude=80.6067, location_name="Кабанбай")

        # Должен вернуться результат из stale кэша
        self.assertEqual(fallback_data["current"]["temperature"], 22.4)


class WeatherApiEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    @patch("apps.weather.services.fetch_open_meteo_data")
    def test_weather_endpoint_exists_and_returns_json(self, mock_fetch):
        """Endpoint /api/weather/ доступен без авторизации и возвращает валидный JSON"""
        mock_fetch.return_value = MOCK_OPEN_METEO_RESPONSE

        url = reverse("weather:weather")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        json_data = response.json()
        self.assertIn("location", json_data)
        self.assertIn("current", json_data)
        self.assertIn("sun", json_data)
        self.assertIn("forecast", json_data)
        self.assertEqual(json_data["location"]["name"], "Кабанбай")
        self.assertEqual(json_data["current"]["temperature"], 22.4)
        self.assertEqual(json_data["current"]["description"], "Преимущественно ясно")

    @patch("apps.weather.services.fetch_open_meteo_data")
    def test_weather_endpoint_custom_coordinates(self, mock_fetch):
        """Endpoint принимает кастомные lat/lon/name через GET-параметры"""
        mock_fetch.return_value = MOCK_OPEN_METEO_RESPONSE

        url = reverse("weather:weather") + "?lat=46.0&lon=81.0&name=Коктума"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["location"]["name"], "Коктума")
        self.assertEqual(json_data["location"]["latitude"], 46.0)
        self.assertEqual(json_data["location"]["longitude"], 81.0)
