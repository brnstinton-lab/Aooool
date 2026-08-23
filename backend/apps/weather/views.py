from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET
from .services import get_weather


@require_GET
def weather_api(request: HttpRequest) -> JsonResponse:
    """
    Публичный API-эндпоинт погоды: GET /api/weather/
    Возвращает текущую погоду, астрономические данные и прогноз на 5-7 дней.
    Не требует авторизации.
    """
    lat_param = request.GET.get('lat')
    lon_param = request.GET.get('lon')
    name_param = request.GET.get('name')

    latitude = None
    longitude = None

    if lat_param is not None:
        try:
            latitude = float(lat_param)
        except (ValueError, TypeError):
            latitude = None

    if lon_param is not None:
        try:
            longitude = float(lon_param)
        except (ValueError, TypeError):
            longitude = None

    weather_data = get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=name_param
    )

    return JsonResponse(weather_data, safe=False, json_dumps_params={'ensure_ascii': False})
