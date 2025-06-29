from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
from app.database import init_db, get_session
from app.models import Session, SessionStatus
from app.services import save_uploaded_image, generate_content_flow, get_video_url
from app.utils import get_settings, logger

app = FastAPI()
settings = get_settings()


@asynccontextmanager
async def startup():
    try:
        logger.info("Starting application initialization")
        init_db()
        db = get_session()

        # Recover pending sessions
        pending_sessions = db.query(Session).filter(
            Session.status != SessionStatus.COMPLETED,
            Session.status != SessionStatus.FAILED
        ).all()

        logger.info(f"Found {len(pending_sessions)} pending sessions to recover")

        for session in pending_sessions:
            logger.info(f"Restarting processing for session {session.id}")
            generate_content_flow.delay(session.id)

        logger.info("Application startup completed")
    except Exception as e:
        logger.critical(f"Application startup failed: {str(e)}")
        raise
    finally:
        if db:
            db.close()


class UploadResponse(BaseModel):
    session_id: str


@app.post("/upload", response_model=UploadResponse)
async def upload_image(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
):
    session_id = str(uuid.uuid4())
    db = get_session()
    try:
        logger.info(f"Starting upload for new session: {session_id}")

        # Save session to DB
        db_session = Session(id=session_id, status=SessionStatus.UPLOADED)
        db.add(db_session)
        db.commit()

        # Save uploaded image
        image_path = save_uploaded_image(file, session_id)
        db_session.image_path = image_path
        db.commit()

        # Start background processing
        # background_tasks.add_task(generate_content_flow.delay, session_id)
        generate_content_flow(session_id)
        logger.info(f"Upload completed for session {session_id}")

        return UploadResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"Upload failed for session {session_id}: {str(e)}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Image upload failed")
    finally:
        if db:
            db.close()


@app.get("/video/{session_id}")
async def get_video(session_id: str):
    db = get_session()
    try:
        session = db.query(Session).filter_by(id=session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.status == SessionStatus.COMPLETED:
            video_url = get_video_url(session.video_task_id)
            return {"url": video_url}
        elif session.video_task_id:
            video_url = get_video_url(session.video_task_id)
            if video_url:
                session.video_path = video_url
                session.status = SessionStatus.COMPLETED
                db.commit()
            return {"url": video_url}
        else:
            return {"status": session.status}
    finally:
        db.close()


# @app.get("/status/{session_id}")
# async def get_status(session_id: str):
#     db = get_session()
#     try:
#         session = db.query(Session).filter_by(id=session_id).first()
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
#
#         if session.video_task_id:
#             video_url = get_video_url(session.video_task_id)
#             generation_status = get_video_generation_status(session.video_task_id)
#             if video_url:
#                 session.video_path = video_url
#                 session.status = SessionStatus.COMPLETED
#                 db.commit()
#
#             response = {
#                 "session_id": session_id,
#                 "status": session.status.value,
#                 "product_name": session.product_name,
#                 "progress": {
#                     "product_name": session.product_name,
#                     "prompt": session.prompt,
#                     "video_ready": session.status == SessionStatus.COMPLETED
#                 }, "video_task": {
#                     "task_id": session.video_task_id,
#                     "last_checked": session.last_checked.isoformat() if session.last_checked else None,
#                     "generation_status": generation_status,
#                 }
#             }
#
#             return response
#         else:
#             return {"status", session.status}
#     finally:
#         db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
