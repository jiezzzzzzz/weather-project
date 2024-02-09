import unittest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from .views import WeatherAPIView


class WeatherAPITestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = WeatherAPIView.as_view()

    @patch('requests.get')
    @patch('geopy.geocoders.Nominatim.geocode')
    def test_get_weather_success(self, mock_geocode, mock_requests_get):
        city_name = 'Moscow'
        request = self.factory.get('/api/weather/', {'city': city_name})

        mock_geocode.return_value.latitude = 55.7558
        mock_geocode.return_value.longitude = 37.6176

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            'fact': {'temp': -5, 'pressure_mm': 765, 'wind_speed': 2}
        }

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('temperature', response.data)
        self.assertIn('pressure', response.data)
        self.assertIn('wind_speed', response.data)

    def test_missing_city_parameter(self):
        request = self.factory.get('/api/weather/')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'City parameter is required')


if __name__ == '__main__':
    unittest.main()