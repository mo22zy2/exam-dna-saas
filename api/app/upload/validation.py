import logging

import redis
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.file import File as FileModel
from app.upload.utils import validate_pdf_content, storage

logger = logging.getLogger(__name__)

_validation_queue = None


def _get_queue():
    global _validation_queue
    if _validation_queue is None:
        from rq import Queue
        conn = redis.from_url(settings.redis_url)
        _validation_queue = Queue("validation", connection=conn, default_timeout=60)
    return _validation_queue


def enqueue_content_validation(file_id: str) -> None:
    from rq import Retry

    queue = _get_queue()
    queue.enqueue(
        "app.upload.validation.validate_file_content",
        file_id,
        retry=Retry(max=3, interval=10),
        job_timeout=60,
    )
    logger.info("Enqueued content validation for file %s", file_id)


def validate_file_content(file_id: str) -> None:
    import asyncio

    db: Session = SessionLocal()
    try:
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            logger.error("File %s not found for validation", file_id)
            return

        content = None
        try:
            content = asyncio.run(storage.read(file_record.storage_key))
        except Exception as e:
            logger.error("Failed to read file %s from storage: %s", file_id, e)
            file_record.validation_status = "rejected"
            db.commit()
            return

        valid, msg = validate_pdf_content(content)
        if valid:
            file_record.validation_status = "validated"
            logger.info("File %s validated successfully", file_id)
        else:
            file_record.validation_status = "rejected"
            logger.warning("File %s rejected: %s", file_id, msg)

        file_record.status = "available" if valid else "rejected"
        db.commit()

    except Exception as e:
        logger.error("Validation job failed for file %s: %s", file_id, e)
        raise
    finally:
        db.close()
