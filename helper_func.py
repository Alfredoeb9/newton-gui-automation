import psutil
import ctypes
import pyautogui
import constants
from fastapi import HTTPException
from pywinauto import Desktop
import newton_gui

def require_admin() -> None:
    if not ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError(
            "Newton GUI API must be run as Administrator for program to see newton software."
        )

# Check if newton is running
def require_newton_running():
    if not newton_gui.is_newton_running():
        raise HTTPException(
            status_code=503,
            detail="Newton.exe is not running"
        )
        
# Grab the PID of newton app
def get_newton_pid() -> int:
    for process in psutil.process_iter(["pid", "name"]):
        try:
            if process.info["name"] == "Newton.exe":
                return process.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    raise RuntimeError("Newton.exe is not running")

# Make the newton app top level (must be running app or terminal as admin)
def activate_newton() -> None:
    pid = get_newton_pid()

    windows = Desktop(backend="win32").windows()

    for window in windows:
        try:
            if window.process_id() == pid and window.window_text() == "Newton":
                window.set_focus()
                return
        except Exception:
            pass

    raise RuntimeError("Newton window not found")

def activate_tab(tab_name: str) -> None:
    coordinates = getattr(constants, tab_name)
    pyautogui.click(coordinates)
    