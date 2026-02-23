import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from pywinauto import mouse, keyboard, win32functions
import cv2
import numpy as np
from PIL import Image, ImageGrab
import mss
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import platform

logger = logging.getLogger(__name__)

class FastUIDetector:
    """Ultra-fast UI element detection and interaction system."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.screen_cache = {}
        self.element_cache = {}
        self.cache_timeout = 2.0  # Cache screenshots for 2 seconds
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Template matching cache
        self.template_cache = {}
        
        # Common UI element templates
        self.ui_templates = self._load_ui_templates()
        
        # Fast screenshot settings
        self.screenshot_region = None  # Full screen by default
        self.screenshot_scale = 0.5  # Scale down for faster processing
        
    def _load_ui_templates(self) -> Dict[str, np.ndarray]:
        """Load common UI element templates."""
        templates = {}
        
        # Create simple templates programmatically for speed
        # These would ideally be loaded from image files
        
        # Button template (simple rectangle)
        button_template = np.ones((30, 100, 3), dtype=np.uint8) * 200
        cv2.rectangle(button_template, (2, 2), (98, 28), (150, 150, 150), 2)
        templates['button'] = button_template
        
        # Text field template
        textfield_template = np.ones((25, 150, 3), dtype=np.uint8) * 255
        cv2.rectangle(textfield_template, (1, 1), (149, 24), (100, 100, 100), 1)
        templates['textfield'] = textfield_template
        
        # Checkbox template
        checkbox_template = np.ones((20, 20, 3), dtype=np.uint8) * 255
        cv2.rectangle(checkbox_template, (2, 2), (18, 18), (0, 0, 0), 2)
        templates['checkbox'] = checkbox_template
        
        return templates
    
    async def take_fast_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Take a fast screenshot using MSS."""
        try:
            # Check cache first
            cache_key = f"screenshot_{region}_{time.time() // self.cache_timeout}"
            if cache_key in self.screen_cache:
                return self.screen_cache[cache_key]
            
            with mss.mss() as sct:
                if region:
                    # Specific region
                    monitor = {
                        "top": region[1],
                        "left": region[0], 
                        "width": region[2] - region[0],
                        "height": region[3] - region[1]
                    }
                else:
                    # Full screen
                    monitor = sct.monitors[1]
                
                # Capture screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img_array = np.array(screenshot)
                
                # Convert BGRA to RGB
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
                
                # Scale down for faster processing if needed
                if self.screenshot_scale < 1.0:
                    height, width = img_rgb.shape[:2]
                    new_height = int(height * self.screenshot_scale)
                    new_width = int(width * self.screenshot_scale)
                    img_rgb = cv2.resize(img_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Cache the result
                self.screen_cache[cache_key] = img_rgb
                
                # Clean old cache entries
                self._clean_cache()
                
                return img_rgb
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return np.array([])
    
    def _clean_cache(self):
        """Clean old cache entries."""
        current_time = time.time()
        current_bucket = current_time // self.cache_timeout
        
        # Remove old screenshot cache entries
        old_keys = [key for key in self.screen_cache.keys() 
                   if not key.endswith(str(int(current_bucket)))]
        for key in old_keys:
            del self.screen_cache[key]
        
        # Remove old element cache entries
        old_element_keys = [key for key, (timestamp, _) in self.element_cache.items() 
                           if current_time - timestamp > self.cache_timeout]
        for key in old_element_keys:
            del self.element_cache[key]
    
    async def find_elements_fast(self, element_types: List[str], 
                                region: Optional[Tuple[int, int, int, int]] = None,
                                confidence: float = 0.8) -> List[Dict[str, Any]]:
        """Find UI elements quickly using template matching."""
        try:
            # Take screenshot
            screenshot = await self.take_fast_screenshot(region)
            if screenshot.size == 0:
                return []
            
            elements = []
            
            # Process each element type
            for element_type in element_types:
                if element_type in self.ui_templates:
                    template = self.ui_templates[element_type]
                    matches = await self._find_template_matches(screenshot, template, confidence)
                    
                    for match in matches:
                        elements.append({
                            'type': element_type,
                            'x': match[0],
                            'y': match[1],
                            'width': template.shape[1],
                            'height': template.shape[0],
                            'confidence': match[2],
                            'center_x': match[0] + template.shape[1] // 2,
                            'center_y': match[1] + template.shape[0] // 2
                        })
            
            return elements
            
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            return []
    
    async def _find_template_matches(self, screenshot: np.ndarray, template: np.ndarray, 
                                   confidence: float) -> List[Tuple[int, int, float]]:
        """Find template matches in screenshot."""
        try:
            # Perform template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            # Find locations where confidence is above threshold
            locations = np.where(result >= confidence)
            
            matches = []
            for pt in zip(*locations[::-1]):  # Switch x and y
                match_confidence = result[pt[1], pt[0]]
                matches.append((pt[0], pt[1], match_confidence))
            
            # Remove overlapping matches (non-maximum suppression)
            matches = self._non_max_suppression(matches, template.shape[:2])
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in template matching: {e}")
            return []
    
    def _non_max_suppression(self, matches: List[Tuple[int, int, float]], 
                           template_size: Tuple[int, int]) -> List[Tuple[int, int, float]]:
        """Remove overlapping matches using non-maximum suppression."""
        if not matches:
            return []
        
        # Sort by confidence (highest first)
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        
        filtered_matches = []
        template_height, template_width = template_size
        
        for match in matches:
            x, y, conf = match
            
            # Check if this match overlaps with any already selected match
            overlaps = False
            for selected_match in filtered_matches:
                sx, sy, _ = selected_match
                
                # Check for overlap
                if (abs(x - sx) < template_width * 0.5 and 
                    abs(y - sy) < template_height * 0.5):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_matches.append(match)
        
        return filtered_matches
    
    async def click_element_fast(self, element: Dict[str, Any], 
                               click_type: str = 'left') -> bool:
        """Click on an element quickly."""
        try:
            x = element.get('center_x', element.get('x', 0))
            y = element.get('center_y', element.get('y', 0))
            
            # Adjust coordinates if screenshot was scaled
            if self.screenshot_scale < 1.0:
                x = int(x / self.screenshot_scale)
                y = int(y / self.screenshot_scale)
            
            # Perform click
            if click_type == 'left':
                mouse.click(coords=(x, y))
            elif click_type == 'right':
                mouse.right_click(coords=(x, y))
            elif click_type == 'double':
                mouse.double_click(coords=(x, y))
            
            logger.info(f"Clicked {click_type} at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False
    
    async def type_text_fast(self, text: str, interval: float = 0.01) -> bool:
        """Type text quickly."""
        try:
            keyboard.send_keys(text, pause=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    async def find_text_fast(self, text: str, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict[str, Any]]:
        """Find text on screen using OCR (simplified implementation)."""
        try:
            # This is a simplified implementation
            # In a full implementation, you would use OCR libraries like pytesseract
            
            # For now, return empty list as OCR is computationally expensive
            # and we're focusing on speed
            return []
            
        except Exception as e:
            logger.error(f"Error finding text: {e}")
            return []
    
    async def wait_for_element(self, element_type: str, timeout: float = 10.0,
                             region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Dict[str, Any]]:
        """Wait for an element to appear."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            elements = await self.find_elements_fast([element_type], region)
            if elements:
                return elements[0]
            
            await asyncio.sleep(0.1)
        
        return None
    
    async def get_screen_regions(self) -> Dict[str, Tuple[int, int, int, int]]:
        """Get common screen regions for faster processing."""
        try:
            # Get screen size
            screen_width, screen_height = win32functions.GetSystemMetrics(0), win32functions.GetSystemMetrics(1)
            
            regions = {
                'full_screen': (0, 0, screen_width, screen_height),
                'top_half': (0, 0, screen_width, screen_height // 2),
                'bottom_half': (0, screen_height // 2, screen_width, screen_height),
                'left_half': (0, 0, screen_width // 2, screen_height),
                'right_half': (screen_width // 2, 0, screen_width, screen_height),
                'center': (screen_width // 4, screen_height // 4, 
                          3 * screen_width // 4, 3 * screen_height // 4),
                'taskbar': (0, screen_height - 50, screen_width, screen_height) if self.system == 'windows' else None,
                'menu_bar': (0, 0, screen_width, 30) if self.system == 'darwin' else None
            }
            
            # Remove None values
            regions = {k: v for k, v in regions.items() if v is not None}
            
            return regions
            
        except Exception as e:
            logger.error(f"Error getting screen regions: {e}")
            return {'full_screen': (0, 0, 1920, 1080)}  # Default fallback
    
    async def analyze_screen_fast(self) -> Dict[str, Any]:
        """Quickly analyze the current screen."""
        try:
            # Take screenshot
            screenshot = await self.take_fast_screenshot()
            if screenshot.size == 0:
                return {}
            
            # Get basic screen info
            height, width = screenshot.shape[:2]
            
            # Find common elements
            common_elements = ['button', 'textfield', 'checkbox']
            elements = await self.find_elements_fast(common_elements)
            
            # Analyze colors (simplified)
            avg_color = np.mean(screenshot, axis=(0, 1))
            
            # Detect if screen is mostly dark or light
            brightness = np.mean(avg_color)
            is_dark_theme = brightness < 128
            
            return {
                'screen_size': (width, height),
                'element_count': len(elements),
                'elements_by_type': {
                    element_type: len([e for e in elements if e['type'] == element_type])
                    for element_type in common_elements
                },
                'average_color': avg_color.tolist(),
                'brightness': brightness,
                'is_dark_theme': is_dark_theme,
                'analysis_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing screen: {e}")
            return {}
    
    def set_screenshot_scale(self, scale: float):
        """Set the screenshot scale for faster processing."""
        if 0.1 <= scale <= 1.0:
            self.screenshot_scale = scale
            logger.info(f"Screenshot scale set to {scale}")
        else:
            logger.warning(f"Invalid scale {scale}, must be between 0.1 and 1.0")
    
    def set_cache_timeout(self, timeout: float):
        """Set the cache timeout."""
        if timeout > 0:
            self.cache_timeout = timeout
            logger.info(f"Cache timeout set to {timeout} seconds")
    
    async def cleanup(self):
        """Clean up resources."""
        self.screen_cache.clear()
        self.element_cache.clear()
        self.executor.shutdown(wait=False)

    async def save_screenshot_to_desktop(self) -> Dict[str, Any]:
        """Take a fast screenshot and save it to the desktop."""
        try:
            start_time = time.time()
            
            with mss.mss() as sct:
                # Take screenshot of primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Save to desktop
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                filename = f"screenshot_{int(time.time())}.png"
                filepath = os.path.join(desktop, filename)
                
                # Ensure directory exists
                os.makedirs(desktop, exist_ok=True)
                
                # Save with mss.tools.to_png
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': f"Screenshot saved to {filepath}",
                'execution_time': execution_time,
                'method': 'screenshot_script',
                'file_path': filepath
            }
            
        except Exception as e:
            logger.error(f"Error saving screenshot to desktop: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'screenshot_script'
            }

# Global fast UI detector instance
fast_ui_detector = FastUIDetector()