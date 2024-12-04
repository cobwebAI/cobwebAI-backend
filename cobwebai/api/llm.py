from cobwebai_lib.audio import Transcription
from cobwebai_lib.text import TextPostProcessing
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from aiofiles import tempfile
from aiofiles import open as aio_open
from openai import AsyncOpenAI
from loguru import logger
from os import path

from cobwebai.auth import current_active_user
from cobwebai.models import User
from cobwebai.settings import settings


SIZE_100MB = 1024 * 1024 * 100
SIZE_1GB = 1024 * 1024 * 1024

openai_client = AsyncOpenAI(api_key=settings.openapi_key)
transcription_provider = Transcription(oai_client=openai_client, log=logger)
postprocessing_provider = TextPostProcessing(oai_client=openai_client, log=logger)

llm_router = APIRouter(prefix="/api/llm")


@llm_router.post("/transcribe")
async def transcribe_file(
    avfile: UploadFile, language: str = "ru", user: User = Depends(current_active_user)
):
    """Transcribes an audio/video file into text"""
    
    if language not in ["ru", "en"]:
        raise HTTPException(400, "Unsupported language")

    if avfile.size > SIZE_1GB:
        raise HTTPException(413, "Input file is too large (>1GB)")

    async with tempfile.TemporaryDirectory() as tempdir:

        named_file_path = path.join(tempdir, avfile.filename)

        async with aio_open(named_file_path, "wb") as named_file:
            # Copy file to file in chunks
            while buf := await avfile.read(SIZE_100MB):
                await named_file.write(buf)

        await avfile.close()

        if text := await transcription_provider.transcribe_file(named_file_path):
            return text
        else:
            raise HTTPException(422, "Failed to process the file")
