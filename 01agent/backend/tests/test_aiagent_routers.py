import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session
from db.models import User, Thread, ThreadStatus, ThreadTask, ThreadTaskStatus, ThreadTaskPlan, ThreadTaskPlanStatus, PlanSubtask, SubtaskStatus, ThreadMessage, ThreadChatType, ThreadChatFromChoices
from schemas.aiagent import NextStepRequest, CurrentSubtaskRequestObj, BackgroundNextStepRequest
from unittest.mock import patch, MagicMock
import json

# Mock the get_llm function from llm_provider
@pytest.fixture(autouse=True)
def mock_llm_provider():
    with patch('utils.llm_provider.get_llm') as mock_get_llm:
        mock_llm_instance = MagicMock()
        mock_llm_instance.ainvoke.return_value = MagicMock(content=json.dumps({"subtasks": [{"subtask": "mock subtask"}]}))
        mock_get_llm.return_value = mock_llm_instance
        yield mock_get_llm

# Mock the upload_helper for prepare_screenshot_for_llm
@pytest.fixture(autouse=True)
def mock_upload_helper():
    with patch('utils.router_helpers.upload_helper') as mock_uh:
        mock_uh.upload_screenshot_s3_bytesio.return_value = "mock_s3_path/screenshot.png"
        yield mock_uh

# Fixture for a working thread and task
@pytest.fixture
def working_thread_and_task(test_session: Session, sample_user: User):
    thread = Thread(user_id=sample_user.id, status=ThreadStatus.WORKING, current_task="Test Task")
    test_session.add(thread)
    test_session.commit()
    test_session.refresh(thread)

    task = ThreadTask(thread_id=thread.id, status=ThreadTaskStatus.WORKING, task_text="Test Task")
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return thread, task

class TestAIAgentRouters:

    @pytest.mark.asyncio
    async def test_current_subtask_request_no_plan(self, client: TestClient, working_thread_and_task, sample_user: User):
        thread, task = working_thread_and_task
        headers = {"Authorization": f"Bearer {sample_user.access_token}"}
        
        request_obj = CurrentSubtaskRequestObj(
            current_os="Windows",
            current_interactive_elements=[],
            current_running_apps=[]
        )

        response = client.post(f"/aiagent/{thread.id}/current_subtask", json=request_obj.model_dump(), headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["subtask_text"] == "mock subtask"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_next_step_desktop_success(self, client: TestClient, working_thread_and_task, sample_user: User):
        thread, task = working_thread_and_task
        headers = {"Authorization": f"Bearer {sample_user.access_token}"}

        # Create a plan and subtask first
        plan = ThreadTaskPlan(thread_task_id=task.id, status=ThreadTaskPlanStatus.ACTIVE)
        test_session.add(plan)
        test_session.commit()
        test_session.refresh(plan)

        subtask = PlanSubtask(thread_task_plan_id=plan.id, subtask_text="Perform desktop action", subtask_type="desktop", ordering=1)
        test_session.add(subtask)
        test_session.commit()
        test_session.refresh(subtask)

        # Mock LLM response for next_step
        with patch('utils.llm_provider.get_llm') as mock_get_llm:
            mock_llm_instance = MagicMock()
            mock_llm_instance.ainvoke.return_value = MagicMock(content=json.dumps({"actions": [{"action": "subtask_completed"}]}))
            mock_get_llm.return_value = mock_llm_instance

            request_obj = NextStepRequest(
                current_os="Windows",
                current_interactive_elements=[],
                current_running_apps=[],
                screenshot_b64="dummy_b64"
            )

            response = client.post(f"/aiagent/{thread.id}/next_step", json=request_obj.model_dump(), headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["actions"][0]["action"] == "subtask_completed"

            # Verify subtask status updated
            test_session.refresh(subtask)
            assert subtask.status == SubtaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_background_next_step_success(self, client: TestClient, working_thread_and_task, sample_user: User):
        thread, task = working_thread_and_task
        headers = {"Authorization": f"Bearer {sample_user.access_token}"}

        # Mock LLM response for background_next_step
        with patch('utils.llm_provider.get_llm') as mock_get_llm:
            mock_llm_instance = MagicMock()
            mock_llm_instance.ainvoke.return_value = MagicMock(content=json.dumps({"actions": [{"action": "task_completed"}]}))
            mock_get_llm.return_value = mock_llm_instance

            request_obj = BackgroundNextStepRequest(
                current_url="http://example.com",
                current_open_tabs=[],
                screenshot_b64="dummy_b64"
            )

            response = client.post(f"/aiagent/background/{thread.id}/next_step", json=request_obj.model_dump(), headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["actions"][0]["action"] == "task_completed"

            # Verify task status updated
            test_session.refresh(task)
            assert task.status == ThreadTaskStatus.COMPLETED