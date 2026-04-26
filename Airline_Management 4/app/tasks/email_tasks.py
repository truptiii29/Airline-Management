import logging
from datetime import datetime, timezone
from celery import shared_task
from app.services.email_service import send_otp_email, send_booking_confirmation, send_cancellation_email
from app.extensions import db, celery
from app.models.aircraft import SeatMap

logger = logging.getLogger(__name__)

@shared_task
def send_otp_email_task(user_id, otp_code, purpose):
    try:
        send_otp_email(user_id, otp_code, purpose)
    except Exception as e:
        logger.error(f"Failed to send OTP email task: {str(e)}")

@shared_task
def send_booking_confirmation_task(booking_id):
    try:
        send_booking_confirmation(booking_id)
    except Exception as e:
        logger.error(f"Failed to send booking confirmation task: {str(e)}")

@shared_task
def send_cancellation_email_task(booking_id):
    try:
        send_cancellation_email(booking_id)
    except Exception as e:
        logger.error(f"Failed to send cancellation email task: {str(e)}")

@shared_task
def cleanup_locks_task():
    try:
        now = datetime.now(timezone.utc)
        seats = SeatMap.query.filter(
            SeatMap.locked_until != None,
            SeatMap.locked_until < now
        ).all()
        
        count = len(seats)
        for seat in seats:
            seat.locked_until = None
            seat.locked_by_user_id = None
            
        db.session.commit()
        logger.info(f"Cleanup locks task released {count} expired locks.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to cleanup locks: {str(e)}")

from datetime import timedelta
celery.conf.beat_schedule = {
    'cleanup-locks-every-5-minutes': {
        'task': 'app.tasks.email_tasks.cleanup_locks_task',
        'schedule': timedelta(minutes=5),
    },
}
