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
        try:
            logger.debug(f"Generating video with prompt: {prompt[:50]}...")
            task_id = hailuo.invoke_video_generation(prompt=prompt)
            return task_id
        except Exception as e:
            logger.error(f"Video task creation error: {str(e)}")
            raise


    def check_video_task_status(self, task_id: str) -> dict:
        try:
            logger.debug(f"Checking video task status: {task_id}")
            status = hailuo.query_video_generation(task_id)
            return {
                "file_id": status[0],
                "status": status[1],
            }
        except Exception as e:
            logger.error(f"Video task status check error: {str(e)}")
            return {"status": "error", "message": str(e)}




    def get_video(self, task_id: str) -> str:
        status =  self.check_video_task_status(task_id=task_id)
        if status['file_id']:
            logger.info(f"found file for task {task_id}")
            try:
                download_url = hailuo.fetch_video_result(file_id=status['file_id'])
                return download_url
            except Exception as e:
                logger.error(f"Video download error: {str(e)}")
                raise
        else:
            return ""