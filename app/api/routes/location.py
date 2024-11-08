from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.api.models.coordinates import Coordinates
from app.services.location_service import LocationService

router = APIRouter()


def get_location_service():
    return LocationService()


@router.post("/location-info")
async def get_location_info(coords: Coordinates,
                            location_service: LocationService = Depends(get_location_service)):
    try:
        if not (-90 <= coords.latitude <= 90 and -180 <= coords.longitude <= 180):
            raise HTTPException(status_code=400, detail="유효하지 않은 GPS 좌표입니다.")

        address = await location_service.get_address(coords)
        nearest_subway = await location_service.get_nearest_subway(coords)
        nearest_busstop = await location_service.check_bus_stop(coords)
        convenience_store_info = await location_service.check_convenience_store(coords)

        return JSONResponse(content={
            "status": "success",
            "data": {
                "address": address,
                "nearest_subway": nearest_subway,
                "convenience_store": convenience_store_info,
                "nearest_busstop": nearest_busstop
            }
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
