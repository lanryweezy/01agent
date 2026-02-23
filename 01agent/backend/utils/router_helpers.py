from sqlmodel import Session, select, and_
from db.models import ThreadMessage, ThreadChatType, ThreadTaskMemoryEntry, ThreadTask, User, Thread, ThreadStatus
import json
from base64 import b64decode
import io
import os
from utils import upload_helper
from typing import Tuple, List, Dict, Optional

def prepare_screenshot_for_llm(screenshot_b64: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Prepares a screenshot for use with a large language model.

    Args:
        screenshot_b64: A base64 encoded screenshot.

    Returns:
        A tuple containing the screenshot user message block and the S3 path if uploaded.
    """
    screenshot_user_message_block = None
    screenshot_s3_path = None
    if screenshot_b64:
        if os.getenv('ENABLE_SCREENSHOT_LOGGING_FOR_TRAINING') == 'true':
            image_bytes = b64decode(screenshot_b64)
            image_io = io.BytesIO(image_bytes)
            screenshot_s3_path = upload_helper.upload_screenshot_s3_bytesio(image_io, extension="png")
        
        if os.getenv('COMPUTER_USE_AGENT_MODEL_TYPE') == 'ollama' or os.getenv('COMPUTER_USE_AGENT_MODEL_TYPE') == 'gemini':
            screenshot_user_message_block = {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{screenshot_b64}"
            }
        else:
            screenshot_user_message_block = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_b64
                }
            }
    return screenshot_user_message_block, screenshot_s3_path

def get_action_history(db: Session, task_id: str, chat_type: ThreadChatType) -> List[Dict]:
    """
    Retrieves the action history for a given task.

    Args:
        db: The database session.
        task_id: The ID of the task.
        chat_type: The type of chat to retrieve history for.

    Returns:
        A list of action history dictionaries.
    """
    action_history = []
    task_previous_messages = db.exec(
        select(ThreadMessage)
        .where(
            and_(
                ThreadMessage.thread_task_id == task_id,
                ThreadMessage.thread_chat_type == chat_type,
            )
        )
        .order_by(ThreadMessage.created_at.desc())
        .limit(5)
    ).all()
    for previous_message in task_previous_messages:
        previous_action_dict = json.loads(previous_message.text)
        action_history.append(previous_action_dict)
    return action_history

def get_memory_items(db: Session, task: ThreadTask, user_id: str) -> List[Dict]:
    """
    Retrieves memory items for a given task.

    Args:
        db: The database session.
        task: The task to retrieve memory for.
        user_id: The ID of the user.

    Returns:
        A list of memory item dictionaries.
    """
    if task.needs_memory_from_previous_tasks:
        tasks_for_memory = db.exec(select(ThreadTask).where(and_(
            ThreadTask.thread.has(Thread.user_id == user_id),
            ThreadTask.thread.has(Thread.status != ThreadStatus.DELETED),
        )).order_by(ThreadTask.created_at.desc()).limit(5)).all()
        tasks_for_memory_ids = [t.id for t in tasks_for_memory]
        memory_items_query = select(ThreadTaskMemoryEntry).where(
            ThreadTaskMemoryEntry.thread_task_id.in_(tasks_for_memory_ids)
        )
    else:
        memory_items_query = select(ThreadTaskMemoryEntry).where(
            ThreadTaskMemoryEntry.thread_task_id == task.id
        )
    
    memory_items = db.exec(memory_items_query).all()
    
    memory_items_arr = []
    for memory_item in memory_items:
        memory_items_arr.append({
            'memory_item_text': memory_item.text,
        })
    return memory_items_arr