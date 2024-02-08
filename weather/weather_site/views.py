import requests
from django.http import JsonResponse
from geopy.geocoders import Nominatim
from environs import Env

env = Env()
env.read_env()


def get_weather(request):
    city_name = request.GET.get('city')

    if not city_name:
        return JsonResponse(
            {
                'error': 'City parameter is required'
            },
            status=400
        )

    try:
        locator = Nominatim(user_agent="myapp")
        location = locator.geocode(city_name, language='ru')

        if location:
            lat = location.latitude
            lon = location.longitude
            api_key = env('API_KEY')
            url = (f'https://api.weather.yandex.ru/v2/forecast/'
                   f'?lat={lat}&lon={lon}&lang=ru_RU&limit=1&hours=false&extra=false')

            headers = {
                'X-Yandex-API-Key': api_key
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                fact = data['fact']

                temperature = fact.get('temp')
                pressure = fact.get('pressure_mm')
                wind_speed = fact.get('wind_speed')

                return JsonResponse(
                    {
                        'temperature': temperature,
                        'pressure': pressure,
                        'wind_speed': wind_speed
                    }
                    )
            else:
                return JsonResponse(
                    {
                        'error': 'Failed to fetch weather data - Yandex response code: '
                                 + str(response.status_code)
                    },
                    status=response.status_code
                )

    except Exception as e:
        return JsonResponse(
            {
                'error': str(e)
            },
            status=500
        )
