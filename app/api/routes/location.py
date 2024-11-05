from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.api.models.coordinates import Coordinates
from app.services.location_service import location_service

router = APIRouter()


@router.post("/location-info")
async def get_location_info(coords: Coordinates):
    try:
        if not (-90 <= coords.latitude <= 90 and -180 <= coords.longitude <= 180):
            raise HTTPException(status_code=400, detail="유효하지 않은 GPS 좌표입니다.")

        address = await location_service.get_address(coords)
        nearest_subway = await location_service.get_nearest_subway(coords)
        has_convenience_store = await location_service.check_convenience_store(coords)
        has_bus_stop = await location_service.check_bus_stop(coords)

        return JSONResponse(content={
            "status": "success",
            "data": {
                "address": address,
                "nearest_subway": nearest_subway,
                "has_convenience_store": has_convenience_store,
                "has_bus_stop": has_bus_stop
            }
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
