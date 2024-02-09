from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.cache import cache
from geopy.geocoders import Nominatim
import requests
from django.conf import settings
from environs import Env

env = Env()
env.read_env()


class WeatherAPIView(APIView):

    def get(self, request):
        city_name = request.GET.get('city')

        if not city_name:
            return Response(
                {
                    'error': 'City parameter is required'
                },
                status=400
            )

        cached_data = cache.get(city_name)

        if cached_data:
            return Response(cached_data)

        try:
            locator = Nominatim(user_agent="myapp")
            location = locator.geocode(city_name, language='ru')

            if location:
                lat = location.latitude
                lon = location.longitude
                api_key = env('API_KEY')
                url = (f'https://api.weather.yandex.ru/v2/forecast/'
                       f'?lat={lat}&lon={lon}&lang=ru_RU&limit=1&hours=false&extra=false')

                headers = {'X-Yandex-API-Key': api_key}
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    fact = data['fact']

                    temperature = fact.get('temp')
                    pressure = fact.get('pressure_mm')
                    wind_speed = fact.get('wind_speed')

                    weather = {
                        'temperature': temperature,
                        'pressure': pressure,
                        'wind_speed': wind_speed
                    }

                    cache.set(city_name, weather, timeout=1800)

                    return Response(weather)

                else:
                    return Response(
                        {
                            'error': f'Failed to fetch weather data - Yandex response code: '
                                     f'{response.status_code}'
                        },
                        status=response.status_code
                    )

            else:
                return Response(
                    {
                        'error': 'City not found'
                    },
                    status=404
                )

        except Exception as e:
            return Response(
                {
                    'error': str(e)
                },
                status=500
            )
