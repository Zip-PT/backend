import requests
from fastapi import HTTPException
from app.core.config import settings


class LocationService:
    def __init__(self):
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": settings.NAVER_CLIENT_ID,
            "X-NCP-APIGW-API-KEY": settings.NAVER_CLIENT_SECRET
        }

    async def get_address(self, coords):
        url = f"https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc?coords={
            coords.longitude},{coords.latitude}&output=json"
        response = await self._make_request(url)

        if not response.get('results'):
            raise HTTPException(
                status_code=404, detail="해당 좌표의 주소를 찾을 수 없습니다.")

        return self._format_address(response['results'][0])

    async def get_nearest_subway(self, coords):
        # ... subway station logic ...
        pass

    async def check_convenience_store(self, coords):
        # ... convenience store logic ...
        pass

    async def check_bus_stop(self, coords):
        # ... bus stop logic ...
        pass

    async def _make_request(self, url):
        response = requests.get(url, headers=self.headers)
        self._handle_response_status(response)
        return response.json()

    def _handle_response_status(self, response):
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="API 호출 한도를 초과했습니다.")
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="네이버 API 인증에 실패했습니다.")
        response.raise_for_status()


location_service = LocationService()
