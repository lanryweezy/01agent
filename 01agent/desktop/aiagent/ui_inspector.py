import pywinauto
import time
import sys
import ctypes
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Windows API to get the active window handle
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow


def inspect_active_window(wait_time=5, filter_text=None, filter_control_type=None):
    """
    Inspects the currently active window and its child UI elements.
    Prints automation_id, class_name, rectangle coordinates for AI-agent targeting.
    """
    try:
        print(Fore.YELLOW + f"Switch to the application you want to inspect within {wait_time} seconds...")
        time.sleep(wait_time)

        # Get active window handle
        hwnd = GetForegroundWindow()
        if not hwnd:
            print(Fore.RED + "Could not get active window handle.")
            return

        # Connect to the window
        app = pywinauto.Application(backend="uia").connect(handle=hwnd)
        window_spec = app.window(handle=hwnd)
        window = window_spec.wrapper_object()

        # Header info
        print(Fore.CYAN + f"\n--- Inspecting Window: {window.window_text()} ---")
        try:
            print(Fore.MAGENTA + f"Control Type: {window.control_type()}")
        except AttributeError:
            print(Fore.RED + "[!] Control type not available.")
        try:
            print(Fore.MAGENTA + f"Class Name: {window.class_name()}")
        except AttributeError:
            print(Fore.RED + "[!] Class name not available.")
        try:
            print(Fore.MAGENTA + f"Automation ID: {window.automation_id()}")
        except AttributeError:
            print(Fore.RED + "[!] Automation ID not available.")

        rect = window.rectangle()
        print(Fore.MAGENTA + f"Rectangle: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
        print(Fore.CYAN + "-" * 60)

        # Inspect child controls
        for i, child in enumerate(window.descendants()):
            try:
                if not child.is_visible() or not child.is_enabled():
                    continue

                # Apply filtering
                if filter_text and filter_text.lower() not in child.window_text().lower():
                    continue
                if filter_control_type and filter_control_type.lower() != child.control_type().lower():
                    continue

                rect = child.rectangle()
                print(Fore.GREEN + f"[Control {i+1}]")
                print(f"  {Fore.WHITE}Text: {Fore.YELLOW}{child.window_text()}")
                print(f"  {Fore.WHITE}Control Type: {Fore.YELLOW}{child.control_type()}")
                print(f"  {Fore.WHITE}Class Name: {Fore.YELLOW}{child.class_name()}")
                print(f"  {Fore.WHITE}Automation ID: {Fore.YELLOW}{child.automation_id()}")
                print(f"  {Fore.WHITE}Rectangle: {Fore.YELLOW}({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
                print(f"  {Fore.WHITE}Is Enabled: {Fore.YELLOW}{child.is_enabled()}")
                print(f"  {Fore.WHITE}Is Visible: {Fore.YELLOW}{child.is_visible()}")
                print(Fore.CYAN + "-" * 60)

            except Exception as e:
                print(Fore.RED + f"[!] Could not inspect child control: {e}")

    except pywinauto.findwindows.ElementNotFoundError:
        print(Fore.RED + "No active window found or could not connect. Ensure an application is active.")
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    try:
        wait = int(input("Enter wait time in seconds before inspection (default 5): ") or 5)
        text_filter = input("Enter text filter (leave blank for none): ").strip() or None
        type_filter = input("Enter control type filter (leave blank for none): ").strip() or None

        inspect_active_window(wait_time=wait, filter_text=text_filter, filter_control_type=type_filter)
        print(Fore.GREEN + "\nInspection complete. You can close this terminal window.")
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Inspection cancelled by user.")
        sys.exit(0)
