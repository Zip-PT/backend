from fastapi import APIRouter, Depends
from app.services.weather_service import WeatherService
from app.api.models.coordinates import Coordinates
router = APIRouter()


def get_weather_service():
    return WeatherService()


@router.post("/weather")
async def get_weather(
        coords: Coordinates,
        weather_service: WeatherService = Depends(get_weather_service)):
    """
    GPS 좌표로 현재 위치의 날씨 정보를 조회합니다.

    - **coords**: 위도/경도 좌표
    """
    return await weather_service.get_weather_by_coords(coords)
