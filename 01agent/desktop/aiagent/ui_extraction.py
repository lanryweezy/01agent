import platform
import pyautogui
import psutil
import os

if platform.system() == "Windows":
    import win32gui
    import win32process

# Windows: UIA
try:
    import uiautomation as auto
except ImportError:
    auto = None

# macOS: Accessibility
try:
    from Quartz import (
        AXUIElementCreateSystemWide,
        AXUIElementCopyAttributeValue,
        kAXRoleAttribute,
        kAXTitleAttribute,
        kAXValueAttribute,
        kAXChildrenAttribute,
    )
except ImportError:
    AXUIElementCreateSystemWide = None

# Linux: AT-SPI
try:
    import pyatspi
except ImportError:
    pyatspi = None


def get_bounding_rect(x, y, width, height):
    screen_w, screen_h = pyautogui.size()
    scale_x = 1280 / screen_w
    scale_y = 720 / screen_h

    scaled_x = int(x * scale_x)
    scaled_y = int(y * scale_y)
    scaled_width = int(width * scale_x)
    scaled_height = int(height * scale_y)

    return {
        'x': int(scaled_x + scaled_width / 2),
        'y': int(scaled_y + scaled_height / 2),
        'width': scaled_width,
        'height': scaled_height,
    }


def get_running_apps():
    system = platform.system()
    result = []

    if system == "Windows":
        # Cache common system processes to filter out
        ignored = frozenset([
            "System Idle Process", "System", "Registry", "MemCompression",
            "svchost.exe", "explorer.exe", "fontdrvhost.exe", "dwm.exe",
            "winlogon.exe", "csrss.exe", "wininit.exe", "services.exe",
            "dllhost.exe", "conhost.exe", "RuntimeBroker.exe", "taskhostw.exe",
            "SearchHost.exe", "ShellExperienceHost.exe", "StartMenuExperienceHost.exe",
            "ApplicationFrameHost.exe", "TextInputHost.exe", "sihost.exe",
            "ctfmon.exe", "SecurityHealthSystray.exe", "SecurityHealthService.exe"
        ])

        def callback(hwnd, app_list):
            if not win32gui.IsWindowVisible(hwnd) or not win32gui.GetWindowText(hwnd):
                return True

            try:
                # Get style and extended style
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

                # Skip tool windows and windows without proper styles
                if (ex_style & win32con.WS_EX_TOOLWINDOW) or \
                   not (style & win32con.WS_VISIBLE) or \
                   not (style & win32con.WS_OVERLAPPEDWINDOW):
                    return True

                # Get process info efficiently
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                name = process.name()

                # Quick checks for ignored processes
                if name in ignored or not name.lower().endswith(".exe"):
                    return True

                # Get window placement for minimized state
                placement = win32gui.GetWindowPlacement(hwnd)
                is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED

                # Get window rect for size check
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    if width < 50 or height < 50:  # Skip tiny windows
                        return True
                except:
                    pass

                entry = {
                    "pid": pid,
                    "name": name,
                    "title": win32gui.GetWindowText(hwnd),
                    "focused": hwnd == win32gui.GetForegroundWindow(),
                    "minimized": is_minimized
                }

                # Use set for faster duplicate checking
                if pid not in app_list["seen_pids"]:
                    app_list["apps"].append(entry)
                    app_list["seen_pids"].add(pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                if isinstance(e, (psutil.NoSuchProcess, psutil.AccessDenied)):
                    return True  # Skip invalid processes silently
                print(f"[❌] Error processing window {hwnd}: {e}")
            return True

        app_data = {"apps": [], "seen_pids": set()}
        try:
            win32gui.EnumWindows(callback, app_data)
            result = app_data["apps"]
        except Exception as e:
            print(f"[❌] Error enumerating windows: {e}")
            result = []

    elif system == "Darwin":
        import subprocess, json
        try:
            output = subprocess.check_output(
                ["osascript", "-e", 'tell application "System Events" to get name of (processes where background only is false)']
            )
            active = subprocess.check_output(
                ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true']
            ).decode().strip()

            apps = [name.strip() for name in output.decode().split(",")]
            result = [{"pid": None, "name": app, "focused": app == active} for app in apps]
        except Exception:
            pass

    elif system == "Linux":
        try:
            import subprocess
            output = subprocess.check_output(["wmctrl", "-lp"]).decode()
            lines = output.splitlines()
            active_output = subprocess.check_output(["xdotool", "getactivewindow", "getwindowpid"]).decode().strip()
            active_pid = int(active_output) if active_output.isdigit() else None

            seen = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = int(parts[2])
                    if pid in seen:
                        continue
                    seen.add(pid)
                    name = psutil.Process(pid).name()
                    result.append({
                        "pid": pid,
                        "name": name,
                        "focused": pid == active_pid
                    })
        except Exception:
            pass

    return result


def extract_desktop_icons_windows():
    """
    Enumerate desktop icons via the Explorer ListView (SysListView32).
    Optimized for performance with caching and error handling.
    """
    if os.getenv('01AGENT_BACKGROUND_MODE') == 'true':
        return []

    if not auto:
        return []

    try:
        # Set shorter timeout for faster response
        auto.SetGlobalSearchTimeout(0.5)
        
        # Find the desktop window first with faster timeout
        desktop = auto.WindowControl(ClassName='WorkerW', searchDepth=1)
        if not desktop.Exists(0):
            desktop = auto.WindowControl(ClassName='Progman', searchDepth=1)
            if not desktop.Exists(0):
                return []
        
        # Locate the SysListView32 control with direct path
        listview = desktop.ListControl(ClassName='SysListView32', searchDepth=2)
        if not listview.Exists(0):
            return []
            
        # Pre-allocate list for better performance
        children = listview.GetChildren()
        if not children:
            return []
            
        icons = [None] * len(children)
        screen_w, screen_h = pyautogui.size()
        valid_count = 0
        
        for item in children:
            try:
                # Quick validation before expensive operations
                if not item.IsEnabled or item.IsOffscreen:
                    continue
                    
                name = item.Name
                if not name or not name.strip():
                    continue
                    
                rect = item.BoundingRectangle
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                
                # Skip tiny or oversized icons
                if w < 20 or h < 20 or w > screen_w/4 or h > screen_h/4:
                    continue
                    
                # Skip icons outside visible area
                if rect.left < 0 or rect.top < 0 or rect.right > screen_w or rect.bottom > screen_h:
                    continue
                    
                icons[valid_count] = {
                    'id': valid_count + 1,
                    'type': 'DesktopIcon',
                    'label': name.strip(),
                    'bounding_box': get_bounding_rect(rect.left, rect.top, w, h),
                }
                valid_count += 1
                
            except Exception as e:
                if 'timeout' in str(e).lower():
                    continue
                continue
                
        return icons[:valid_count] if valid_count > 0 else []
        
    except Exception as e:
        print(f"[❌] Desktop icon extraction error: {e}")
        return []


def extract_ui_elements_windows():
    """
    Extract UI Automation interactive elements from all visible windows.
    Optimized for performance with caching and error handling.
    """
    if not auto:
        return []
    
    try:
        # Set shorter timeout for faster response
        auto.SetGlobalSearchTimeout(1.0)
        desktop = auto.GetDesktopControl()
        elements = []
        screen_w, screen_h = pyautogui.size()
        max_elements = 1000  # Limit total elements
        
        # Optimized interactive control types set
        interactive = frozenset([
            "ButtonControl", "EditControl", "CheckBoxControl", "ComboBoxControl",
            "HyperlinkControl", "TabItemControl", "MenuItemControl", "ListItemControl",
            "TreeItemControl", "SpinnerControl", "SliderControl", "ProgressBarControl",
            "ListControl", "TableControl", "TextControl", "SplitButtonControl"
        ])

        def process_element(control, depth=0, max_depth=6):
            if depth > max_depth or len(elements) >= max_elements:
                return
                
            try:
                # Fast validation
                if not control.IsEnabled or control.IsOffscreen:
                    return
                    
                control_type = control.ControlTypeName
                if not control_type or control_type not in interactive:
                    return
                    
                rect = control.BoundingRectangle
                x, y = rect.left, rect.top
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                
                # Skip invalid elements
                if w <= 5 or h <= 5 or w > screen_w * 0.9 or h > screen_h * 0.9:
                    return
                    
                if x < 0 or y < 0 or x + w > screen_w or y + h > screen_h:
                    return
                    
                elements.append({
                    "type": control_type.replace('Control', ''),
                    "label": control.Name or "",
                    "bounding_box": get_bounding_rect(x, y, w, h),
                    "depth": depth
                })
                
                # Process visible windows and their children
                if depth == 0 or control.IsTopLevel():
                    for child in control.GetChildren():
                        process_element(child, depth + 1, max_depth)
                    
            except Exception as e:
                if 'timeout' in str(e).lower():
                    return
                return

        # Process all top-level windows
        for window in desktop.GetChildren():
            try:
                if window.IsEnabled and not window.IsOffscreen:
                    process_element(window)
            except Exception:
                continue
                
        return elements
    except Exception as e:
        print(f"[❌] UI extraction error: {e}")
        return []


def extract_ui_elements_macos():
    """
    Extract macOS Accessibility interactive elements globally.
    Optimized for performance with caching and improved error handling.
    """
    if not AXUIElementCreateSystemWide:
        return []

    try:
        # Cache interactive roles for faster lookup
        interactive = frozenset([
            "AXButton", "AXTextField", "AXCheckBox", "AXComboBox", "AXMenuItem",
            "AXTabGroup", "AXSlider", "AXScrollBar", "AXList", "AXTable",
            "AXPopUpButton", "AXRadioButton", "AXLink", "AXMenu"
        ])

        system = AXUIElementCreateSystemWide()
        elements = []
        screen_w, screen_h = pyautogui.size()

        def recurse(element, depth=0, max_depth=10):
            if depth > max_depth:  # Prevent infinite recursion
                return

            try:
                # Batch property access
                props = {
                    'role': AXUIElementCopyAttributeValue(element, kAXRoleAttribute),
                    'title': AXUIElementCopyAttributeValue(element, kAXTitleAttribute) or "",
                    'value': AXUIElementCopyAttributeValue(element, kAXValueAttribute) or "",
                    'children': AXUIElementCopyAttributeValue(element, kAXChildrenAttribute) or []
                }

                if props['role'] in interactive:
                    try:
                        f = AXUIElementCopyAttributeValue(element, 'AXFrame')
                        x, y, w, h = f.x, f.y, f.width, f.height

                        # Skip invalid or oversized elements
                        if w <= 0 or h <= 0 or w > screen_w or h > screen_h:
                            return

                        # Skip elements outside screen bounds
                        if x < 0 or y < 0 or x + w > screen_w or y + h > screen_h:
                            return

                        elements.append({
                            "type": props['role'].replace('AX', ''),
                            "label": props['title'] or props['value'],
                            "bounding_box": get_bounding_rect(x, y, w, h),
                            "depth": depth
                        })
                    except Exception:
                        pass

                for child in props['children']:
                    recurse(child, depth + 1, max_depth)

            except Exception as e:
                if 'timeout' in str(e).lower():
                    return  # Skip timing out elements
                return  # Skip other errors silently

        recurse(system)
        return elements

    except Exception as e:
        print(f"[❌] macOS UI extraction error: {e}")
        return []


def extract_ui_elements_linux():
    """
    Extract AT-SPI interactive elements on Linux desktop.
    Optimized for performance with caching and improved error handling.
    """
    if not pyatspi:
        return []

    try:
        desktop = pyatspi.Registry.getDesktop(0)
        elements = []
        screen_w, screen_h = pyautogui.size()

        # Cache interactive roles for faster lookup
        interactive = frozenset([
            "push button", "check box", "combo box", "text", "hyperlink", "menu item",
            "slider", "spin button", "tab", "table", "tree item", "list item"
        ])

        def recurse(obj, depth=0, max_depth=10):
            if depth > max_depth:  # Prevent infinite recursion
                return

            try:
                # Batch property access
                props = {
                    'role': obj.getRoleName(),
                    'name': obj.name or "",
                    'states': obj.getState()
                }

                if props['role'].lower() in interactive:
                    try:
                        component = obj.queryComponent()
                        x, y, w, h = component.getExtents(pyatspi.DESKTOP_COORDS)

                        # Skip invalid or oversized elements
                        if w <= 0 or h <= 0 or w > screen_w or h > screen_h:
                            return

                        # Skip elements outside screen bounds
                        if x < 0 or y < 0 or x + w > screen_w or y + h > screen_h:
                            return

                        elements.append({
                            "type": props['role'].title().replace(' ', ''),
                            "label": props['name'],
                            "bounding_box": get_bounding_rect(x, y, w, h),
                            "depth": depth
                        })
                    except Exception:
                        pass

                # Get children in batch
                try:
                    children = [obj.getChildAtIndex(i) for i in range(obj.childCount)]
                    for child in children:
                        if child:
                            recurse(child, depth + 1, max_depth)
                except Exception:
                    pass

            except Exception as e:
                if 'timeout' in str(e).lower():
                    return  # Skip timing out elements
                return  # Skip other errors silently

        recurse(desktop)
        return elements

    except Exception as e:
        print(f"[❌] Linux UI extraction error: {e}")
        return []


def detect_possible_webview(bounding_boxes, screen_w, screen_h, threshold=0.5):
    """
    Detect if a large portion of the screen is uncovered, suggesting a WebView.
    Returns a placeholder element if so. Optimized for performance.
    """
    if not bounding_boxes:
        return {
            "id": -1,
            "type": "PossibleWebView",
            "label": "Potential WebView region - no UI elements detected",
            "bounding_box": {
                "x": int(screen_w * 0.05),
                "y": int(screen_h * 0.05),
                "width": int(screen_w * 0.9),
                "height": int(screen_h * 0.9),
            },
        }

    total_area = screen_w * screen_h
    covered = sum(
        bb["width"] * bb["height"]
        for box in bounding_boxes
        if (bb := box.get("bounding_box")) and bb["width"] and bb["height"]
    )

    if (1 - (covered / total_area)) >= threshold:
        return {
            "id": -1,
            "type": "PossibleWebView",
            "label": "Potential WebView region - large uncovered area",
            "bounding_box": {
                "x": int(screen_w * 0.05),
                "y": int(screen_h * 0.05),
                "width": int(screen_w * 0.9),
                "height": int(screen_h * 0.9),
            },
        }

    return None


from functools import lru_cache
import threading

@lru_cache(maxsize=1)
def get_cached_ui_elements():
    """
    Get cached UI elements with a short TTL to avoid excessive UI queries.
    The cache is automatically invalidated after 100ms.
    """
    system = platform.system()
    raw = []

    try:
        if system == "Windows":
            ui = extract_ui_elements_windows()
            icons = []
            if not ui:
                icons = extract_desktop_icons_windows()
            raw = ui + icons
        elif system == "Darwin":
            raw = extract_ui_elements_macos()
        elif system == "Linux":
            raw = extract_ui_elements_linux()
        else:
            raise NotImplementedError(f"Unsupported platform: {system}")

        # Schedule cache invalidation
        def invalidate_cache():
            get_cached_ui_elements.cache_clear()
        threading.Timer(0.1, invalidate_cache).start()
        
        return raw
    except Exception as e:
        print(f"[❌] UI element extraction error: {e}")
        return []

def extract_interactive_elements():
    """
    Combine native elements with caching and optimized processing.
    Returns a list of dicts: {id, type, label, bounding_box}.
    """
    raw = get_cached_ui_elements()
    if not raw:
        return []
    
    # Pre-allocate list for better performance
    interactive = [None] * len(raw)
    screen_w, screen_h = pyautogui.size()
    
    # Filter and process elements efficiently
    valid_count = 0
    for e in raw:
        try:
            # Skip elements without required properties
            if not all(k in e for k in ('type', 'bounding_box')):
                continue
                
            bb = e.get('bounding_box')
            # Skip elements with invalid bounding boxes
            if not bb or not all(k in bb for k in ('x', 'y', 'width', 'height')):
                continue
                
            # Skip elements with invalid dimensions
            if bb['width'] <= 0 or bb['height'] <= 0:
                continue
                
            # Skip oversized elements
            if bb['width'] > screen_w or bb['height'] > screen_h:
                continue
                
            # Skip elements outside screen bounds
            if bb['x'] < 0 or bb['y'] < 0 or bb['x'] + bb['width'] > screen_w or bb['y'] + bb['height'] > screen_h:
                continue
                
            # Add valid element to the list
            interactive[valid_count] = {
                'id': valid_count + 1,
                'type': e['type'],
                'label': e.get('label', '').strip(),
                'bounding_box': bb
            }
            valid_count += 1
            
        except Exception:
            continue
    
    # Trim the list to actual size
    interactive = interactive[:valid_count] if valid_count > 0 else []
    
    # Check for webview
    webview_hint = detect_possible_webview(interactive, screen_w, screen_h)
    if webview_hint:
        interactive.append(webview_hint)
        
    return interactive
