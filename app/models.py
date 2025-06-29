from enum import Enum
from sqlalchemy import Column, String, Enum as SQLEnum, LargeBinary, DateTime

from app.database import Base


class SessionStatus(str, Enum):
    UPLOADED = "UPLOADED"
    RECOGNIZING = "RECOGNIZING"
    GENERATING_PROMPT = "GENERATING_PROMPT"
    VIDEO_TASK_CREATED = "VIDEO_TASK_CREATED"
    VIDEO_GENERATING = "VIDEO_GENERATING"
    VIDEO_READY = "VIDEO_READY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, index=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.UPLOADED)
    image_data = Column(LargeBinary)
    product_name = Column(String(100))
    prompt = Column(String(500))
    video_path = Column(String(255))
    video_task_id = Column(String(100))
    last_checked = Column(DateTime)
