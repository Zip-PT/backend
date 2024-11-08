import requests
from fastapi import HTTPException
from app.core.config import settings
from typing import Optional, Dict, Any

from math import radians, sin, cos, sqrt, atan2


class LocationService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.language = "ko"

    async def get_address(self, coords) -> str:
        """좌표를 주소로 변환"""
        url = f"{self.base_url}/geocode/json"
        params = {
            'latlng': f"{coords.latitude},{coords.longitude}",
            'language': self.language,
            'key': self.api_key
        }

        response = await self._make_request(url, params)

        if not response.get('results'):
            raise HTTPException(
                status_code=404, detail="해당 좌표의 주소를 찾을 수 없습니다.")

        # 가장 상세한 주소 반환
        return response['results'][0]['formatted_address']

    async def get_nearest_subway(self, coords) -> Optional[Dict[str, Any]]:
        """가장 가까운 지하철역 검색"""
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            'location': f"{coords.latitude},{coords.longitude}",
            'radius': 2000,  # 2km 반경
            'type': 'subway_station',
            'language': self.language,
            # 'keyword': '역',  # 더 정확한 검색을 위해 추가
            'key': self.api_key
        }

        response = await self._make_request(url, params)

        if not response.get('results'):
            return None

        nearest_station = response['results'][0]
        station_location = nearest_station['geometry']['location']

        # 직선 거리 계산
        distance = self._calculate_distance(
            coords.latitude,
            coords.longitude,
            station_location['lat'],
            station_location['lng']
        )

        # 평균 도보 속도를 대충 4km/h(1.1m/s)로 잡고 시간 계산
        walking_time_minutes = round(distance / (4000/60))

        # 역 이름에서 '역' 글자가 없으면 추가
        station_name = nearest_station['name']
        if not station_name.endswith('역'):
            station_name += '역'

        return {
            'name': station_name,
            'distance': distance,
            'distance_unit': '미터',
            'walking_time': int(walking_time_minutes * 1.2),
            'time_unit': '분',
            'location': {
                'lat': station_location['lat'],
                'lng': station_location['lng']
            }
        }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 지점 간의 직선 거리를 미터 단위로 계산 (Haversine formula)"""
        R = 6371000  # 지구 반경 (미터)

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return round(distance)

    async def check_convenience_store(self, coords) -> bool:
        """300m 반경 내 편의점 존재 여부"""
        url = f"{self.base_url}/place/nearbysearch/json"

        range = 200

        params = {
            'location': f"{coords.latitude},{coords.longitude}",
            'radius': range,
            'type': 'convenience_store',
            'language': self.language,
            'key': self.api_key
        }

        response = await self._make_request(url, params)

        results = response.get('results')
        count = len(results)

        return {
            "count": count,
            "range": f'{range}m'
        }

    async def check_bus_stop(self, coords) -> bool:
        """300m 반경 내 버스정류장 존재 여부"""
        url = f"{self.base_url}/place/nearbysearch/json"

        range = 500

        params = {
            'location': f"{coords.latitude},{coords.longitude}",
            'radius': range,
            'type': 'bus_station',
            'language': self.language,
            'key': self.api_key
        }

        response = await self._make_request(url, params)
        results = response.get('results')
        count = len(results)

        return {
            "count": count,
            "range": f'{range}m'
        }

    async def _make_request(self, url: str, params: Dict[str, str]) -> Dict[str, Any]:
        """API 요청 공통 처리"""
        try:
            response = requests.get(url, params=params)
            self._handle_response_status(response)
            data = response.json()

            if data.get('status') == 'OVER_QUERY_LIMIT':
                raise HTTPException(
                    status_code=429, detail="API 호출 한도를 초과했습니다.")
            elif data.get('status') == 'REQUEST_DENIED':
                raise HTTPException(
                    status_code=401, detail="Google Maps API 인증에 실패했습니다.")
            elif data.get('status') not in ['OK', 'ZERO_RESULTS']:
                raise HTTPException(
                    status_code=500,
                    detail=f"Google Maps API 오류: {data.get('status')}"
                )

            return data

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"외부 API 호출 중 오류가 발생했습니다: {str(e)}"
            )

    def _handle_response_status(self, response: requests.Response) -> None:
        """HTTP 응답 상태 처리"""
        if response.status_code == 429:
            raise HTTPException(status_code=429, detail="API 호출 한도를 초과했습니다.")
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401, detail="Google Maps API 인증에 실패했습니다.")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="요청한 리소스를 찾을 수 없습니다.")
        response.raise_for_status()
