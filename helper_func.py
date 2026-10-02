import psutil
import ctypes
import pyautogui
import constants
from fastapi import HTTPException
from pywinauto import Desktop
from pathlib import Path
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
    
def buildDataObject(values: dict[str, str]) -> dict[str, str]:
    data = {}

    if "strain" in values:
        data["strain"] = values["strain"] + " in"

    if "strain_rate" in values:
        data["strain_rate"] = values["strain_rate"] + " in/min"

    if "strain_max" in values:
        data["strain_max"] = values["strain_max"] + " in"

    if "position" in values:
        data["position"] = values["position"] + " mm"

    if "position_rate" in values:
        data["position_rate"] = values["position_rate"] + " mm/min"

    if "position_max" in values:
        data["position_max"] = values["position_max"] + " mm"

    if "load" in values:
        data["load"] = values["load"] + " N"

    if "load_rate" in values:
        data["load_rate"] = values["load_rate"] + " N/min"

    if "load_max" in values:
        data["load_max"] = values["load_max"] + " N"

    return data

def copy_string_from_field(x: int, y: int):
    """Clicks on input field box and copys any string in the input field
            
        Parameters
        ----------
        x: int
            The x coordinate of mouse when hovered over box
        y: int
            The y coordinate of mouse when hovered over box
            
        Returns
        -------
        None
    """
    activate_newton()
        
    pyautogui.click(x, y, clicks=3, interval=0.1)
    pyautogui.press("ctrl", "c")

def clear_input_field(x: int, y: int, main_tab: str | None = None) -> None:
    """Clicks on input field box and clears any characters
        
    Parameters
    ----------
    x: int
        The x coordinate of mouse when hovered over box
    y: int
        The y coordinate of mouse when hovered over box
        
    Returns
    -------
    None
    """
    
    activate_newton()
    
    if main_tab is not None:
        activate_tab(str(main_tab))
    
    pyautogui.click(x, y, clicks=3, interval=0.1)
    pyautogui.press("backspace")
    
def extract_batches():
    # Find all .cmm files
    cmm_files = constants.DOWNLOAD_FOLDER.rglob("*.cmm")

    # Remove duplicates based on filename
    unique_files = {}

    for file in cmm_files:
        unique_files[file.stem.lower()] = file

    # Display results
    for file in sorted(unique_files.values(), key=lambda x: x.stem.lower()):
        print(file.stem)

