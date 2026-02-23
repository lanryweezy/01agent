import pytest
import asyncio
import json
import os
from unittest.mock import patch, MagicMock

# Adjust path to import ai_executor from the parent directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_executor import AIExecutor, AIRTEST_TEMPLATE_DIR

@pytest.fixture
def ai_executor_instance():
    """Fixture to provide an AIExecutor instance."""
    # Mock connect_device to prevent actual Airtest connection attempts during tests
    with patch('ai_executor.connect_device'):
        executor = AIExecutor(model="test_model")
        yield executor

@pytest.mark.asyncio
async def test_execute_task_no_screenshot(ai_executor_instance):
    """Test execute_task when no screenshot is provided."""
    result = await ai_executor_instance.execute_task("test task", context={})
    assert not result['success']
    assert "No screenshot provided" in result['error']

@pytest.mark.asyncio
async def test_prepare_prompt(ai_executor_instance):
    """Test _prepare_prompt generates correct prompt."""
    task_description = "Open browser and go to google.com"
    context = {"some_info": "value"}
    prompt = ai_executor_instance._prepare_prompt(task_description, context)
    assert task_description in prompt
    assert "CLICK(x, y, description)" in prompt
    assert "AIRTEST_TOUCH_IMAGE(image_name, confidence)" in prompt
    assert "Return only the action to take, in a JSON format" in prompt

@pytest.mark.asyncio
@patch('ai_executor.ollama.chat')
async def test_get_ai_decision_success(mock_ollama_chat, ai_executor_instance):
    """Test _get_ai_decision returns a valid decision."""
    mock_ollama_chat.return_value = {
        'message': {'content': '{"action": "CLICK", "parameters": {"x": 100, "y": 200}}'}
    }
    prompt = "test prompt"
    screenshot_b64 = "dummy_b64"
    decision = await ai_executor_instance._get_ai_decision(prompt, screenshot_b64)
    assert decision['action'] == "CLICK"
    assert decision['parameters']['x'] == 100
    mock_ollama_chat.assert_called_once()

@pytest.mark.asyncio
@patch('ai_executor.ollama.chat')
async def test_get_ai_decision_ollama_error(mock_ollama_chat, ai_executor_instance):
    """Test _get_ai_decision handles Ollama errors."""
    mock_ollama_chat.side_effect = Exception("Ollama connection error")
    prompt = "test prompt"
    screenshot_b64 = "dummy_b64"
    decision = await ai_executor_instance._get_ai_decision(prompt, screenshot_b64)
    assert decision['action'] == "DONE"
    assert "Ollama connection error" in decision['parameters']['message']

@pytest.mark.asyncio
@patch('ai_executor.pyautogui.click')
async def test_execute_ai_decision_click(mock_pyautogui_click, ai_executor_instance):
    """Test _execute_ai_decision for CLICK action."""
    ai_decision = {"action": "CLICK", "parameters": {"x": 100, "y": 200}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_pyautogui_click.assert_called_once_with(100, 200)

@pytest.mark.asyncio
@patch('ai_executor.pyautogui.typewrite')
async def test_execute_ai_decision_type(mock_pyautogui_typewrite, ai_executor_instance):
    """Test _execute_ai_decision for TYPE action."""
    ai_decision = {"action": "TYPE", "parameters": {"text_to_type": "hello"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_pyautogui_typewrite.assert_called_once_with("hello")

@pytest.mark.asyncio
@patch('ai_executor.pyautogui.scroll')
async def test_execute_ai_decision_scroll(mock_pyautogui_scroll, ai_executor_instance):
    """Test _execute_ai_decision for SCROLL action."""
    ai_decision = {"action": "SCROLL", "parameters": {"direction": "down"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_pyautogui_scroll.assert_called_once_with(-100)

@pytest.mark.asyncio
async def test_execute_ai_decision_wait(ai_executor_instance):
    """Test _execute_ai_decision for WAIT action."""
    ai_decision = {"action": "WAIT", "parameters": {"seconds": 0.1}}
    start_time = asyncio.get_event_loop().time()
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    end_time = asyncio.get_event_loop().time()
    assert result['success']
    assert (end_time - start_time) >= 0.1

@pytest.mark.asyncio
@patch('ai_executor.touch')
async def test_execute_ai_decision_airtest_touch(mock_airtest_touch, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_TOUCH action."""
    ai_decision = {"action": "AIRTEST_TOUCH", "parameters": {"x": 10, "y": 20, "description": "icon"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_airtest_touch.assert_called_once_with((10, 20))

@pytest.mark.asyncio
@patch('ai_executor.swipe')
async def test_execute_ai_decision_airtest_swipe(mock_airtest_swipe, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_SWIPE action."""
    ai_decision = {"action": "AIRTEST_SWIPE", "parameters": {"x1": 10, "y1": 20, "x2": 30, "y2": 40}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_airtest_swipe.assert_called_once_with((10, 20), (30, 40), duration=0.8)

@pytest.mark.asyncio
@patch('ai_executor.text')
async def test_execute_ai_decision_airtest_text(mock_airtest_text, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_TEXT action."""
    ai_decision = {"action": "AIRTEST_TEXT", "parameters": {"text_to_type": "test input"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_airtest_text.assert_called_once_with("test input")

@pytest.mark.asyncio
@patch('ai_executor.snapshot')
async def test_execute_ai_decision_airtest_snapshot(mock_airtest_snapshot, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_SNAPSHOT action."""
    ai_decision = {"action": "AIRTEST_SNAPSHOT", "parameters": {"filename": "test.png"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_airtest_snapshot.assert_called_once_with(filename="test.png")

@pytest.mark.asyncio
@patch('ai_executor.os.path.exists', return_value=True)
@patch('ai_executor.touch')
async def test_execute_ai_decision_airtest_touch_image(mock_airtest_touch, mock_exists, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_TOUCH_IMAGE action."""
    ai_decision = {"action": "AIRTEST_TOUCH_IMAGE", "parameters": {"image_name": "button.png", "confidence": 0.9}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert result['success']
    mock_exists.assert_called_once_with(os.path.join(AIRTEST_TEMPLATE_DIR, "button.png"))
    mock_airtest_touch.assert_called_once()

@pytest.mark.asyncio
@patch('ai_executor.os.path.exists', return_value=False)
async def test_execute_ai_decision_airtest_touch_image_not_found(mock_exists, ai_executor_instance):
    """Test _execute_ai_decision for AIRTEST_TOUCH_IMAGE action when image not found."""
    ai_decision = {"action": "AIRTEST_TOUCH_IMAGE", "parameters": {"image_name": "non_existent.png"}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert not result['success']
    assert "Image template not found" in result['error']
    mock_exists.assert_called_once_with(os.path.join(AIRTEST_TEMPLATE_DIR, "non_existent.png"))

@pytest.mark.asyncio
async def test_execute_ai_decision_unknown_action(ai_executor_instance):
    """Test _execute_ai_decision for an unknown action."""
    ai_decision = {"action": "UNKNOWN_ACTION", "parameters": {}}
    result = await ai_executor_instance._execute_ai_decision(ai_decision)
    assert not result['success']
    assert "Unknown action" in result['error']