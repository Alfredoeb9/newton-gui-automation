import pyautogui
import time
import psutil
from pathlib import Path
import constants

# NEWTON_TEST_DIR = Path(
#     r"C:\Users\TRI Test Machine\AppData\Local\Newton\Tests"
# )

# # Maybe move this to a different file to track all global constant variables
# MM_JOG_HIGH_SPEED_BOX_X_COORD = 570
# MM_JOG_HIGH_SPEED_BOX_Y_COORD = 540
# MM_JOG_LOW_SPEED_BOX_X_COORD = 742
# MM_JOG_LOW_SPEED_BOX_Y_COORD = 542
# MM_JOG_HOME_RATE_BOX_X_COORD = 900
# MM_JOG_HOME_RATE_BOX_Y_COORD = 540
# MM_JOG_HOME_POSITION_BOX_X_COORD = 1056
# MM_JOG_HOME_POSITION_BOX_Y_COORD = 538
# ONLINE_FILTER_TAB_X_COORD = 374
# ONLINE_FILTER_TAB_Y_COORD = 213
# ONLINE_START_STOP_BTN_X_COORD = 1523
# ONLINE_START_STOP_BTN_Y_COORD = 315
# ONLINE_POS_TARE_BTN_X_COORD = 766
# ONLINE_POS_TARE_BTN_Y_COORD = 315
# ONLINE_LOAD_TARE_BTN_X_COORD = 975
# ONLINE_LOAD_TARE_BTN_Y_COORD = 421
# ONLINE_STRESS_TARE_BTN_X_COORD = 1183
# ONLINE_STRESS_TARE_BTN_Y_COORD = 421
# ONLINE_PAUSE_RESUME_BTN_X_COORD = 1500
# ONLINE_PAUSE_RESUME_BTN_Y_COORD = 367
# HIGHLIGHT_BOX_CLICK = 3

# START_FLAG = False
# IS_PAUSED = False

def health():
    print("Testing health ")
    
def is_newton_running() -> bool:

    for process in psutil.process_iter(["name"]):

        try:
            if process.info["name"] == "Newton.exe":
                return True

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            pass

    return False

# GET /tests -> returns available .tst configs
# POST /tests/select -> JSON: { "name": "Flexure Strength Test-RT 20-40mm"}
# GUI automation selects/loads that config in Newton
def get_filters() -> list[dict[str, str]]:
    filterArray: list[dict[str, str]] = []
    
    for filter in constants.NEWTON_TEST_DIR.glob("*.tst"):
        filterArray.append({"name": filter.stem, "file": filter.name})

    return filterArray

# Machine Management Tab
def set_jog_high_speed(speed: int) -> None:
    pyautogui.click(*constants.MM_JOG_HIGH_SPEED_BOX, *constants.HIGHLIGHT_BOX_CLICK)
    pyautogui.write(str(speed))
    pyautogui.press("enter")
     
        
# Machine Management Tab
def set_jog_low_speed(speed: int) -> None:
    pyautogui.click(*constants.MM_JOG_LOW_SPEED_BOX, constants.HIGHLIGHT_BOX_CLICK)
    pyautogui.write(str(speed))
    pyautogui.press("enter")
     

# Machine Management Tab
def set_home_rate(speed: int) -> None:
    try:
        pyautogui.click(*constants.MM_JOG_HOME_RATE_BOX, constants.HIGHLIGHT_BOX_CLICK)
        pyautogui.write(str(speed))
        pyautogui.press("enter")
    except:
        print("Error setting home_rate on the machine management tab")        

# Machine Management Tab
def set_home_position(pos) -> None:
    try:
        pyautogui.click(*constants.MM_JOG_HOME_POSITION_BOX, constants.HIGHLIGHT_BOX_CLICK)
        pyautogui.write(str(pos))
        pyautogui.press("enter")
    except:
        print("Error setting home_position on the machine management tab")        

# Online Tab
def clear_pos_tare() -> None:
    try:
        pyautogui.click(*constants.ONLINE_POS_TARE_BTN)
        print("Ch:Position has been tared")
    except:
        print("Error taring CH:Pos on the online tab")        
    
# Online Tab
def clear_load_tare() -> None:
    try:
        pyautogui.click(*constants.ONLINE_LOAD_TARE_BTN)
        print("Ch:Load has been tared")
    except:
        print("Error taring CH:Load on the online tab")
        
# Online Tab
def clear_stress_tare() -> None:
    try:
        pyautogui.click(*constants.ONLINE_STRESS_TARE_BTN)
        print("Ch:Stress has been tared")
    except:
        print("Error taring CH:Stress on the online tab")       
    
# Online Tab
# Presses the jog up high button for a given amount of seconds
def jog_up_high(seconds: int) -> None:
    pyautogui.moveTo(*constants.ONLINE_JOG_UP_HIGH_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")

# Online Tab
# Presses the jog down high button for a given amount of seconds
def jog_down_high(seconds: int) -> None:
    pyautogui.moveTo(*constants.ONLINE_JOG_DOWN_HIGH_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")

def clear_input_field(x: int, y: int) -> None:
    pyautogui.click(x, y, clicks=3, interval=0.1)
    pyautogui.press("backspace")
    
# Online Tab
# Places the filter option into the online filter tab
def set_filter_online_tab(filter_name: str) -> None:
    clear_input_field(*constants.ONLINE_FILTER_TAB)
    # pyautogui.click(ONLINE_FILTER_TAB_X_COORD, ONLINE_FILTER_TAB_Y_COORD)
    pyautogui.write(str(filter_name))
    pyautogui.press("enter")

        
# Online Tab
def start_test() -> None:
    # if (START_FLAG == False):
    #     START_FLAG = True
        print("Starting test ... ")
        pyautogui.click(*constants.ONLINE_START_STOP_BTN)

def stop_test() -> None:
    # if (START_FLAG):
    #     START_FLAG = False
        print("Stopping test ... ")
        pyautogui.click(*constants.ONLINE_START_STOP_BTN)

# Online Tab
def pause_resume_btn() -> None:
    pyautogui.click(*constants.ONLINE_PAUSE_RESUME_BTN)


