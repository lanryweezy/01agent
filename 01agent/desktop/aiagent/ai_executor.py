import logging
import asyncio
import json
import os # Import os module for path joining
from typing import Dict, Any, List
import ollama
from pywinauto.application import Application
from pywinauto import mouse, keyboard, win32functions
from airtest.core.api import * # Import Airtest API
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type # Import tenacity

from config.settings import settings # Import settings
from backend.utils.llm_provider import get_llm # Import get_llm

logger = logging.getLogger(__name__)

# Define the directory for Airtest image templates
AIRTEST_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "airtest_templates")

class AIExecutor:
    """
    An intelligent task executor that uses a multimodal AI model
    to understand the screen and execute tasks.
    """

    def __init__(self):
        logger.info(f"Initializing AI Executor with model {settings.computer_use_agent_model_id}...")
        self.model = settings.computer_use_agent_model_id
        self.llm = get_llm(agent="computer_use") # Get the LLM instance
        # Connect to Windows desktop for Airtest
        try:
            connect_device("Windows:///")
            logger.info("Airtest connected to Windows desktop.")
        except Exception as e:
            logger.warning(f"Could not connect Airtest to Windows desktop: {e}. Airtest commands might not work.")


    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a task using the multimodal AI model.
        """
        logger.info(f"AI Executor received task: {task_description}")
        context = context or {}

        screenshot_b64 = context.get('screenshot_b64')
        if not screenshot_b64:
            return {
                'success': False,
                'error': 'No screenshot provided in the context.',
                'method': 'ai_executor_error'
            }

        prompt = self._prepare_prompt(task_description, context)
        
        # Prepare messages for LangChain's invoke method
        messages = [
            {
                'role': 'user',
                'content': prompt,
                'images': [screenshot_b64]
            }
        ]

        ai_decision = await self._get_ai_decision(messages)
        result = await self._execute_ai_decision(ai_decision)

        return result

    def _prepare_prompt(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Prepares the prompt for the multimodal model.
        """
        prompt = f"""
        You are an AI assistant controlling a computer.
        The user wants to perform the following task: "{task_description}".
        
        Based on the provided screenshot, what is the next action to take?
        
        Analyze the screen and determine the best action. The action should be one of the following:
        - CLICK(x, y, description)
        - TYPE(text_to_type)
        - SCROLL(direction)
        - WAIT(seconds)
        - DONE(message)
        - CLICK_ELEMENT(title, control_type, description) - Use this to click on a UI element identified by its properties.
        - TYPE_IN_ELEMENT(title, control_type, text_to_type, description) - Use this to type text into a UI element identified by its properties.
        - SCROLL_ELEMENT(title, control_type, direction, description) - Use this to scroll a UI element identified by its properties.
        - AIRTEST_TOUCH(x, y, description)
        - AIRTEST_SWIPE(x1, y1, x2, y2, duration)
        - AIRTEST_TEXT(text_to_type)
        - AIRTEST_SNAPSHOT(filename)
        - AIRTEST_TOUCH_IMAGE(image_name, confidence) - Use this to click on an element identified by an image template. image_name refers to a file in the 'airtest_templates' directory. Confidence is a float between 0 and 1 (default 0.8).
        
        Example Image Templates (place these files in desktop/aiagent/airtest_templates/):
        - login_button.png
        - settings_icon.png
        - search_bar.png
        - minimize_window.png
        - close_button.png
        
        Example for CLICK_ELEMENT:
        {
            "action": "CLICK_ELEMENT",
            "parameters": {
                "title": "OK Button",
                "control_type": "Button",
                "description": "the OK button in a dialog"
            }
        }
        
        Example for TYPE_IN_ELEMENT:
        {
            "action": "TYPE_IN_ELEMENT",
            "parameters": {
                "title": "Username Field",
                "control_type": "Edit",
                "text_to_type": "myusername",
                "description": "the username input field"
            }
        }
        
        Example for SCROLL_ELEMENT:
        {
            "action": "SCROLL_ELEMENT",
            "parameters": {
                "title": "Scrollable Area",
                "control_type": "Pane",
                "direction": "down",
                "description": "a scrollable content area"
            }
        }
        
        Return only the action to take, in a JSON format like:
        {
            "action": "CLICK",
            "parameters": {
                "x": 100,
                "y": 200,
                "description": "a button"
            }
        }
        """
        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
    async def _get_ai_decision(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calls the multimodal model to get the next action.
        """
        logger.info("Calling multimodal AI model...")
        response = await self.llm.ainvoke(messages) # Use ainvoke for async
        decision_str = response.content
        logger.info(f"AI decision: {decision_str}")
        decision = json.loads(decision_str)
        return decision

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
    async def _execute_ai_decision(self, ai_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the action decided by the AI.
        """
        action = ai_decision.get("action")
        parameters = ai_decision.get("parameters", {})
        
        logger.info(f"Executing AI decision: {action} with parameters {parameters}")

        if action == "CLICK":
            x = parameters.get("x")
            y = parameters.get("y")
            if x is not None and y is not None:
                mouse.click(coords=(x, y))
                return {
                    "success": True,
                    "output": f"Clicked at ({x}, {y})",
                    "method": "ai_executor_click"
                }
            else:
                return {"success": False, "error": "Missing x or y for CLICK action"}
        elif action == "TYPE":
            text = parameters.get("text_to_type")
            if text is not None:
                keyboard.send_keys(text)
                return {
                    "success": True,
                    "output": f"Typed text: {text}",
                    "method": "ai_executor_type"
                }
            else:
                return {"success": False, "error": "Missing text_to_type for TYPE action"}
        elif action == "SCROLL":
            direction = parameters.get("direction")
            if direction is not None:
                pos = win32functions.GetCursorPos()
                mouse.scroll(coords=pos, wheel_dist=-1 if direction == "down" else 1)
                return {
                    "success": True,
                    "output": f"Scrolled {direction}",
                    "method": "ai_executor_scroll"
                }
            else:
                return {"success": False, "error": "Missing direction for SCROLL action"}
        elif action == "CLICK_ELEMENT":
            title = parameters.get("title")
            control_type = parameters.get("control_type")
            description = parameters.get("description", "element")
            if title is not None and control_type is not None:
                try:
                    app = Application(backend="uia").connect(title_re=f".*{title}.*")
                    window = app.window(title_re=f".*{title}.*")
                    control = window.child_window(control_type=control_type)
                    control.click_input()
                    return {
                        "success": True,
                        "output": f"Clicked {description} (Title: {title}, ControlType: {control_type})",
                        "method": "ai_executor_click_element"
                    }
                except Exception as e:
                    return {"success": False, "error": f"Failed to click element: {e}"}
            else:
                return {"success": False, "error": "Missing title or control_type for CLICK_ELEMENT action"}
        elif action == "TYPE_IN_ELEMENT":
            title = parameters.get("title")
            control_type = parameters.get("control_type")
            text_to_type = parameters.get("text_to_type")
            description = parameters.get("description", "element")
            if title is not None and control_type is not None and text_to_type is not None:
                try:
                    app = Application(backend="uia").connect(title_re=f".*{title}.*")
                    window = app.window(title_re=f".*{title}.*")
                    control = window.child_window(control_type=control_type)
                    control.set_text(text_to_type)
                    return {
                        "success": True,
                        "output": f"Typed '{text_to_type}' into {description} (Title: {title}, ControlType: {control_type})",
                        "method": "ai_executor_type_in_element"
                    }
                except Exception as e:
                    return {"success": False, "error": f"Failed to type into element: {e}"}
            else:
                return {"success": False, "error": "Missing title, control_type, or text_to_type for TYPE_IN_ELEMENT action"}
        elif action == "SCROLL_ELEMENT":
            title = parameters.get("title")
            control_type = parameters.get("control_type")
            direction = parameters.get("direction")
            description = parameters.get("description", "element")
            if title is not None and control_type is not None and direction is not None:
                try:
                    app = Application(backend="uia").connect(title_re=f".*{title}.*")
                    window = app.window(title_re=f".*{title}.*")
                    control = window.child_window(control_type=control_type)
                    if direction == "down":
                        control.scroll("down")
                    elif direction == "up":
                        control.scroll("up")
                    elif direction == "left":
                        control.scroll("left")
                    elif direction == "right":
                        control.scroll("right")
                    return {
                        "success": True,
                        "output": f"Scrolled {description} {direction} (Title: {title}, ControlType: {control_type})",
                        "method": "ai_executor_scroll_element"
                    }
                except Exception as e:
                    return {"success": False, "error": f"Failed to scroll element: {e}"}
            else:
                return {"success": False, "error": "Missing title, control_type, or direction for SCROLL_ELEMENT action"}
        elif action == "WAIT":
            seconds = parameters.get("seconds")
            if seconds is not None:
                await asyncio.sleep(seconds)
                return {
                    "success": True,
                    "output": f"Waited for {seconds} seconds",
                    "method": "ai_executor_wait"
                }
            else:
                return {"success": False, "error": "Missing seconds for WAIT action"}
        elif action == "DONE":
            return {
                "success": True,
                'output': parameters.get("message", "Task completed."),
                "method": "ai_executor_done"
            }
        elif action == "AIRTEST_TOUCH":
            x = parameters.get("x")
            y = parameters.get("y")
            description = parameters.get("description", "element")
            if x is not None and y is not None:
                touch((x, y))
                return {
                    "success": True,
                    "output": f"Airtest touched {description} at ({x}, {y})",
                    "method": "ai_executor_airtest_touch"
                }
            else:
                return {"success": False, "error": "Missing x or y for AIRTEST_TOUCH action"}
        elif action == "AIRTEST_SWIPE":
            x1 = parameters.get("x1")
            y1 = parameters.get("y1")
            x2 = parameters.get("x2")
            y2 = parameters.get("y2")
            duration = parameters.get("duration", 0.8)
            if all(v is not None for v in [x1, y1, x2, y2]):
                swipe((x1, y1), (x2, y2), duration=duration)
                return {
                    "success": True,
                    "output": f"Airtest swiped from ({x1}, {y1}) to ({x2}, {y2})",
                    "method": "ai_executor_airtest_swipe"
                }
            else:
                return {"success": False, "error": "Missing coordinates for AIRTEST_SWIPE action"}
        elif action == "AIRTEST_TEXT":
            text_to_type = parameters.get("text_to_type")
            if text_to_type is not None:
                text(text_to_type)
                return {
                    "success": True,
                    "output": f"Airtest typed text: {text_to_type}",
                    "method": "ai_executor_airtest_text"
                }
            else:
                return {"success": False, "error": "Missing text_to_type for AIRTEST_TEXT action"}
        elif action == "AIRTEST_SNAPSHOT":
            filename = parameters.get("filename", f"snapshot_{int(time.time())}.png")
            snapshot(filename=filename)
            return {
                "success": True,
                "output": f"Airtest took snapshot: {filename}",
                "method": "ai_executor_airtest_snapshot"
            }
        elif action == "AIRTEST_TOUCH_IMAGE":
            image_name = parameters.get("image_name")
            confidence = parameters.get("confidence", 0.8)
            if image_name is not None:
                image_path = os.path.join(AIRTEST_TEMPLATE_DIR, image_name)
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Image template not found: {image_path}") # Raise exception for retry
                
                # Perform touch using image template
                touch(Template(image_path, threshold=confidence))
                return {
                    "success": True,
                    "output": f"Airtest touched image: {image_name} with confidence {confidence}",
                    "method": "ai_executor_airtest_touch_image"
                }
            else:
                return {"success": False, "error": "Missing image_name for AIRTEST_TOUCH_IMAGE action"}
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "method": "ai_executor_error"
            }

# Global AI executor instance
ai_executor = AIExecutor()