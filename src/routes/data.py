from fastapi import FastAPI , APIRouter , Depends , UploadFile , status
from fastapi.responses import JSONResponse
import logging
from helpers.config import get_settings , Settings
from controllers import DataController
import aiofiles
from models import ResponseSignal

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id : str,file : UploadFile, app_settings: Settings = Depends(get_settings)):
    is_valid ,result_signal = DataController().validate_uploaded_file(file = file)

    if not is_valid:
        logger.warning(f"File validation failed for project {project_id}: {result_signal.value}")
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : result_signal.value,
            }
        )

    file_path , file_id = DataController().generate_unique_filepath(orig_file_name = file.filename , project_id = project_id)

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)

    logger.info(f"File uploaded successfully for project {project_id}: {file_id}")

    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id,
        }
    )