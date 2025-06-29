import os
from datetime import datetime

import requests
from celery import Celery

from .database import get_session
from .models import Session, SessionStatus
from .utils import get_settings, logger
from .video_generator_dummy import VideoGenerator

settings = get_settings()
celery = Celery(__name__, broker=settings.broker_url)

video_generator = VideoGenerator()


def save_uploaded_image(file, session_id: str) -> str:
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{session_id}.jpg"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        logger.info(f"Image saved for session {session_id} at {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving image for session {session_id}: {str(e)}")
        raise


@celery.task
def generate_content_flow(session_id: str):
    db = get_session()
    try:
        session = db.query(Session).filter_by(id=session_id).first()
        if not session:
            logger.warning(f"Session {session_id} not found")
            return
        logger.info(f"Started generation flow for session: {session_id}")

        # Восстановление с последнего статуса
        # Этап 1: Распознавание продукта
        if session.status in [SessionStatus.UPLOADED, SessionStatus.RECOGNIZING]:
            logger.info(f"Starting recognition for session {session_id}")
            session.status = SessionStatus.RECOGNIZING
            db.commit()

            if not session.product_name:
                session.product_name = recognize_product(session.image_data)
                logger.success(f"Recognized product: {session.product_name}")

            session.status = SessionStatus.GENERATING_PROMPT
            db.commit()

        # Этап 2: Генерация промпта
        if session.status == SessionStatus.GENERATING_PROMPT:
            logger.info(f"Generating prompt for session {session_id}")
            session.status = SessionStatus.GENERATING_PROMPT
            db.commit()

            if not session.prompt:
                session.prompt = generate_prompt(session.product_name)
                logger.success(f"Generated prompt: {session.prompt[:50]}...")

            session.status = SessionStatus.VIDEO_TASK_CREATED
            db.commit()

        # Этап 3: Создание задачи генерации видео
        if session.status == SessionStatus.VIDEO_TASK_CREATED:
            logger.info(f"Creating video task for session {session_id}")
            session.status = SessionStatus.VIDEO_TASK_CREATED
            db.commit()

            if not session.video_task_id:
                session.video_task_id = video_generator.create_video_task(session.prompt, session.image_data)
                session.status = SessionStatus.VIDEO_GENERATING
                session.last_checked = datetime.now()
                db.commit()


    except Exception as e:
        logger.error(f"Error processing session {session_id}: {str(e)}")
        session.status = SessionStatus.FAILED
        db.commit()
    finally:
        db.close()


def recognize_product(image_path: str) -> str:
    try:
        logger.debug(f"NOT IMPLEMENTED | Calling recognition API with image {image_path}")
        return "UNKNOWN"
    except requests.exceptions.RequestException as e:
        logger.error(f"Recognition API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in recognition: {str(e)}")
        raise


def generate_prompt(product_name: str) -> str:
    try:
        logger.debug(f"Generating prompt for product: {product_name}")

        template_path = "templates/prompt_template.txt"
        if not os.path.exists(template_path):
            logger.error(f"Prompt template not found at {template_path}")
            raise FileNotFoundError(f"Prompt template not found")

        with open(template_path, "r") as f:
            template = f.read()

        if product_name != "UNKNOWN":
            prompt = template.format(product_name=product_name)
        else:
            prompt = template
        return prompt
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        raise


def get_video_generation_status(task_id: str):
    return video_generator.check_video_task_status(task_id=task_id)


def get_video_url(task_id: str):
    return video_generator.get_video(task_id=task_id)
