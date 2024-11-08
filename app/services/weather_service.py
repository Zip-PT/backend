import requests
from fastapi import HTTPException
from app.core.config import settings
from app.services.location_service import LocationService


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org"

    async def get_lat_lon(self, city_name: str) -> tuple:
        """도시 이름으로 위도/경도 조회"""
        try:
            response = requests.get(
                f'{self.base_url}/geo/1.0/direct',
                params={
                    'q': city_name,
                    'appid': self.api_key
                }
            ).json()

            if not response:
                raise HTTPException(
                    status_code=404,
                    detail=f"도시 '{city_name}'를 찾을 수 없습니다."
                )

            data = response[0]
            return data.get('lat'), data.get('lon')

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"위치 정보 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_weather_by_coords(self, coords) -> dict:
        """GPS 좌표로 날씨 정보 조회"""
        try:
            # Google Maps API로 도시 이름 조회
            location_service = LocationService()
            city_name = await location_service.get_city_name(coords)

            # OpenWeather API로 날씨 정보 조회
            response = requests.get(
                f'{self.base_url}/data/2.5/weather',
                params={
                    'lat': coords.latitude,
                    'lon': coords.longitude,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'kr'  # 한국어 응답
                }
            ).json()

            if "weather" not in response or "main" not in response:
                raise HTTPException(
                    status_code=404,
                    detail=f"해당 위치의 날씨 정보를 찾을 수 없습니다."
                )

            return {
                "city": city_name,
                "weather": {
                    "description": response['weather'][0]['description'],
                    "icon": f"https://openweathermap.org/img/w/{response['weather'][0]['icon']}.png"
                },
                "temperature": {
                    "current": round(response['main']['temp'], 1),
                    "feels_like": round(response['main']['feels_like'], 1),
                },
                "humidity": response['main']['humidity']
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"날씨 정보 조회 중 오류가 발생했습니다: {str(e)}"
            )
