import os
from datetime import datetime

import requests
import uuid
import time
from .database import get_session
from .models import Session, SessionStatus
from .utils import get_settings, logger
from celery import Celery
from .llm import hailuo

settings = get_settings()
celery = Celery(__name__, broker=settings.broker_url)

class VideoGenerator():

    def create_video_task(self, prompt: str, image_data: bytes) -> str:
        return "123456789"

    def check_video_task_status(self, task_id: str) -> dict:
        try:
            logger.debug(f"Checking video task status: {task_id}")
            return {
                "file_id": "1",
                "status": "Finished",
            }
        except Exception as e:
            logger.error(f"Video task status check error: {str(e)}")
            return {"status": "error", "message": str(e)}




    def get_video(self, task_id: str) -> str:
        download_url = "https://uss3.dreamfaceapp.com/server/common/work/ed5e9c98d9fa4604bcf5452c6b440899.mp4"
        return download_url
