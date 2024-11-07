from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.audio_service import AudioService

router = APIRouter()

# Dependency Injection을 위함


def get_audio_service():
    return AudioService()


@router.post("/summarise-audio")
async def transcribe_and_summarize(audio_file: UploadFile = File(...),
                                   audio_service: AudioService = Depends(get_audio_service)):
    try:
        if not audio_file.filename.endswith(('.mp3', '.wav', '.m4a')):
            raise HTTPException(
                status_code=400, detail="지원하지 않는 오디오 파일 형식입니다.")
        result = await audio_service.process_audio(audio_file)
        return JSONResponse(content={"status": "success", **result})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
