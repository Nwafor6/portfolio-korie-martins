from datetime import datetime
import json
import logging
from celery import shared_task
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from support.helpers import sendMail

logger = logging.getLogger(__name__)


@shared_task
def run_daily_streak_recording():
    """
    Task to record daily streaks for all users.
    This task will run at midnight every day.
    """
    # call the func from the task
    # func()
