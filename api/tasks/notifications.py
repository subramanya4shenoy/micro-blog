import time
from celery_app import celery_app
from logging_config import get_logger
from celery import shared_task
import random

logger = get_logger("tasks.notificarions")

@celery_app.task
def send_new_post_notification(post_id: int, title: str):
    logger.info(f"[celery] Starting notification tasks for post_id = {post_id}")
    time.sleep(2)
    logger.info(f"[celery] Finished sending notification tasks for post_id = {post_id}")
    return {"status": "ok", "post_id": post_id}


# @shared_task(
#     name="tasks.notifications.send_new_post_notification",
#     autoretry_for=(Exception,),  
#     retry_backoff=5,     
#     retry_kwargs={"max_retries": 3},
# )
# def send_new_post_notification(post_id: int, user_id: int):
#     logger.info(f"[celery] Starting notification tasks for post_id = {post_id}")

#     if random.random() < 0.5:
#         logger.error("[celery] Simulated failure for post_id=%s", post_id)
#         raise RuntimeError("Simulated notification failure")

#     logger.info(f"[celery] Finished sending notification tasks for post_id = {post_id}")
#     return {"status": "ok", "post_id": post_id}