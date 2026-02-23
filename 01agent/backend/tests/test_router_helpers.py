import pytest
from sqlmodel import Session
from db.models import ThreadMessage, ThreadChatType, ThreadTask, User, Thread, ThreadStatus, ThreadTaskMemoryEntry
from utils.router_helpers import prepare_screenshot_for_llm, get_action_history, get_memory_items
import json
from unittest.mock import patch, MagicMock

# Mock the upload_helper for prepare_screenshot_for_llm
@pytest.fixture(autouse=True)
def mock_upload_helper():
    with patch('utils.router_helpers.upload_helper') as mock_uh:
        mock_uh.upload_screenshot_s3_bytesio.return_value = "mock_s3_path/screenshot.png"
        yield mock_uh

@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    class MockSession:
        def __init__(self):
            self.messages = []
            self.tasks = []
            self.memory_entries = []

        def exec(self, statement):
            # Simplified mock for select statements
            if "ThreadMessage" in str(statement):
                return MagicMock(first=lambda: None, all=lambda: self.messages)
            elif "ThreadTask" in str(statement):
                return MagicMock(first=lambda: None, all=lambda: self.tasks)
            elif "ThreadTaskMemoryEntry" in str(statement):
                return MagicMock(first=lambda: None, all=lambda: self.memory_entries)
            return MagicMock(first=lambda: None, all=lambda: [])

    return MockSession()


class TestRouterHelpers:

    @pytest.mark.parametrize("model_type, expected_type", [
        ("ollama", "image_url"),
        ("gemini", "image_url"),
        ("openai", "image"),
        (None, None) # No screenshot_b64
    ])
    def test_prepare_screenshot_for_llm(self, model_type, expected_type):
        # Mock os.getenv for COMPUTER_USE_AGENT_MODEL_TYPE
        with patch('utils.router_helpers.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: model_type if key == 'COMPUTER_USE_AGENT_MODEL_TYPE' else default
            
            screenshot_b64 = "dummy_base64_string" if expected_type else None
            block, s3_path = prepare_screenshot_for_llm(screenshot_b64)

            if expected_type:
                assert block['type'] == expected_type
                assert s3_path == "mock_s3_path/screenshot.png"
            else:
                assert block is None
                assert s3_path is None

    def test_get_action_history(self, mock_db_session):
        mock_db_session.messages = [
            ThreadMessage(thread_task_id="task1", thread_chat_type=ThreadChatType.DESKTOP_USE, text=json.dumps({"action": "click1"})),
            ThreadMessage(thread_task_id="task1", thread_chat_type=ThreadChatType.DESKTOP_USE, text=json.dumps({"action": "type1"})),
            ThreadMessage(thread_task_id="task2", thread_chat_type=ThreadChatType.DESKTOP_USE, text=json.dumps({"action": "click2"}))
        ]
        history = get_action_history(mock_db_session, "task1", ThreadChatType.DESKTOP_USE)
        assert len(history) == 2
        assert history[0]["action"] == "click1"
        assert history[1]["action"] == "type1"

    def test_get_memory_items_from_current_task(self, mock_db_session):
        mock_task = ThreadTask(id="task1", needs_memory_from_previous_tasks=False)
        mock_db_session.memory_entries = [
            ThreadTaskMemoryEntry(thread_task_id="task1", text="memory1"),
            ThreadTaskMemoryEntry(thread_task_id="task1", text="memory2")
        ]
        memory = get_memory_items(mock_db_session, mock_task, "user1")
        assert len(memory) == 2
        assert memory[0]["memory_item_text"] == "memory1"

    def test_get_memory_items_from_previous_tasks(self, mock_db_session):
        mock_task = ThreadTask(id="task1", needs_memory_from_previous_tasks=True)
        mock_db_session.tasks = [
            ThreadTask(id="task_prev1", thread=Thread(user_id="user1", status=ThreadStatus.STANDBY)),
            ThreadTask(id="task_prev2", thread=Thread(user_id="user1", status=ThreadStatus.STANDBY))
        ]
        mock_db_session.memory_entries = [
            ThreadTaskMemoryEntry(thread_task_id="task_prev1", text="memory_prev1"),
            ThreadTaskMemoryEntry(thread_task_id="task_prev2", text="memory_prev2")
        ]
        memory = get_memory_items(mock_db_session, mock_task, "user1")
        assert len(memory) == 2
        assert memory[0]["memory_item_text"] == "memory_prev1"