from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.audio_service import audio_service

router = APIRouter()


@router.post("/summarise")
async def transcribe_and_summarize(audio_file: UploadFile = File(...)):
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
