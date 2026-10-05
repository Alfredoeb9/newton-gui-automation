import pyautogui
import time
import psutil
from pathlib import Path
import constants
import helper_func
from ocr import ocr
from datetime import datetime

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

# Online Tab
def configure_specimen(specimen_id: str, specimen_width: int, specimen_depth: int, specimen_guage: int | None = None, specimen_span: int | None = None):
    """configures specimen

    Args:
        specimen_id (str): name or ID given to the specimen
        specimen_width (int): width of the specimen
        specimen_depth (int): depth of the speciment
    """
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    pyautogui.click(*constants.ONLINE_SPECIMEN_CONFIG_BUTTON)
    time.sleep(0.01)
    
    # Paste in users ID name into ID field
    helper_func.clear_input_field(*constants.ONLINE_CONFIG_ID)
    pyautogui.write(str(specimen_id))
    pyautogui.press("enter")
    
    helper_func.clear_input_field(*constants.ONLINE_CONFIG_WIDTH)
    pyautogui.write(str(specimen_width))
    pyautogui.press("enter")
    
    helper_func.clear_input_field(*constants.ONLINE_CONFIG_DEPTH)
    pyautogui.write(str(specimen_depth))
    pyautogui.press("enter")
    
    if specimen_guage is not None:
        helper_func.clear_input_field(*constants.ONLINE_CONFIG_GAUGE)
        pyautogui.write(str(specimen_guage))
        pyautogui.press("enter")
        
    if specimen_span is not None:
            helper_func.clear_input_field(*constants.ONLINE_CONFIG_SPAN)
            pyautogui.write(str(specimen_span))
            pyautogui.press("enter")
    
    pyautogui.click(*constants.ONLINE_CONFIG_ENTER_BTN)

# Machine Management Tab
def set_jog_high_speed(speed: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("MM_MAIN_TAB")
    
    pyautogui.click(*constants.MM_JOG_HIGH_SPEED_BOX, *constants.HIGHLIGHT_BOX_CLICK)
    pyautogui.write(str(speed))
    pyautogui.press("enter")
     
        
# Machine Management Tab
def set_jog_low_speed(speed: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("MM_MAIN_TAB")
    
    pyautogui.click(*constants.MM_JOG_LOW_SPEED_BOX, constants.HIGHLIGHT_BOX_CLICK)
    pyautogui.write(str(speed))
    pyautogui.press("enter")
     

# Machine Management Tab
def set_home_rate(speed: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("MM_MAIN_TAB")
    
    try:
        pyautogui.click(*constants.MM_JOG_HOME_RATE_BOX, constants.HIGHLIGHT_BOX_CLICK)
        pyautogui.write(str(speed))
        pyautogui.press("enter")
    except:
        print("Error setting home_rate on the machine management tab")        

# Machine Management Tab
def set_home_position(pos) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("MM_MAIN_TAB")
    
    try:
        pyautogui.click(*constants.MM_JOG_HOME_POSITION_BOX, constants.HIGHLIGHT_BOX_CLICK)
        pyautogui.write(str(pos))
        pyautogui.press("enter")
    except:
        print("Error setting home_position on the machine management tab")        

# Online Tab
def clear_pos_tare() -> None:
    # helper_func.activate_newton()
    # helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    try:
        pyautogui.click(*constants.ONLINE_POS_TARE_BTN)
        print("Ch:Position has been tared")
    except:
        print("Error taring CH:Pos on the online tab")        
    
# Online Tab
def clear_load_tare() -> None:
    # helper_func.activate_newton()
    # helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    try:
        pyautogui.click(*constants.ONLINE_LOAD_TARE_BTN)
        print("Ch:Load has been tared")
    except:
        print("Error taring CH:Load on the online tab")
        
# Online Tab
def clear_stress_tare() -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    try:
        pyautogui.click(*constants.ONLINE_STRESS_TARE_BTN)
        print("Ch:Stress has been tared")
    except:
        print("Error taring CH:Stress on the online tab")       
    
# Online Tab
# Presses the jog up high button for a given amount of seconds
def jog_up_fast(seconds: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    pyautogui.moveTo(*constants.ONLINE_JOG_UP_FAST_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")
        
# Online Tab
# Presses the jog up low button for a given amount of seconds
def jog_up_slow(seconds: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    pyautogui.moveTo(*constants.ONLINE_JOG_UP_SLOW_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")

# Online Tab
# Presses the jog down high button for a given amount of seconds
def jog_down_fast(seconds: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    pyautogui.moveTo(*constants.ONLINE_JOG_DOWN_FAST_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")
        
# Online Tab
# Presses the jog down slow button for a given amount of seconds
def jog_down_slow(seconds: int) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    
    pyautogui.moveTo(*constants.ONLINE_JOG_DOWN_SLOW_BTN)
    pyautogui.mouseDown(button="left")

    try:
        time.sleep(seconds)
    finally:
        pyautogui.mouseUp(button="left")
    
# Online Tab
# Places the filter option into the online filter tab
def set_filter_online_tab(filter_name: str) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    # time.sleep(0.1)
    
    helper_func.clear_input_field(*constants.ONLINE_FILTER_TAB)
    
    pyautogui.write(str(filter_name))
    pyautogui.press("enter")

        
# Online Tab
def start_test() -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    clear_pos_tare()
    clear_load_tare()
    # if (START_FLAG == False):
    #     START_FLAG = True
    print("Starting test ... ")
    pyautogui.click(*constants.ONLINE_START_STOP_BTN)

def stop_test() -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    # if (START_FLAG):
    #     START_FLAG = False
    print("Stopping test ... ")
    pyautogui.click(*constants.ONLINE_START_STOP_BTN)

# Online Tab
def pause_resume_btn() -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("ONLINE_MAIN_TAB")
    pyautogui.click(*constants.ONLINE_PAUSE_RESUME_BTN)
    
def wait_for_test_complete(specimen_id: str, timeout: int = 3600):
    start_time = time.time()

    while True:
        state = ocr.get_start_stop_state()
        
        print(f"Start check: {state}")

        if state == "stop":
            print("Test has started.")
            break

        if time.time() - start_time > timeout:
            raise TimeoutError(f"Test {specimen_id} never started")

        time.sleep(1)

    # Now we know the test actually started.
    # Wait for Stop -> Start.
    while True:
        state = ocr.get_start_stop_state()
        
        print(f"Test check: {state}")

        if state == "start":
            print("Test has finished.")
            return

        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Test {specimen_id} did not complete"
            )

        time.sleep(5)

# Report Tab
def download_report(batchID) -> None:
    helper_func.activate_newton()
    helper_func.activate_tab("REPORT_MAIN_TAB")
    helper_func.activate_tab("REPORT_DOWNLOAD_TAB")
    
    # include the batchID + "_{date}_{time}"
    # timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
    # batch_id = f"{batchID}_{timestamp}"
    print(f"Downloading batch {batchID}")
    
    pyautogui.click(*constants.REPORT_BATCHES_UNNAMED)
    pyautogui.write(str(batchID))
    pyautogui.press("enter")
    pyautogui.click(*constants.REPORT_DOWNLOAD_REPORT)
    time.sleep(0.5)
    pyautogui.click(*constants.REPORT_DOWNLOAD_COMPLETE_BUTTON)
    
# Report Tab
def extract_report_to_csv(specimen_ID) -> str:
    helper_func.activate_newton()
    helper_func.activate_tab("REPORT_MAIN_TAB")
    helper_func.activate_tab("REPORT_VIEW_TAB")
    
    # include the batchID + "_{date}_{time}"
    # timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
    # batch_id = f"{specimen_ID}_{timestamp}"
    print(f"Downloading csv {specimen_ID}")
    
    pyautogui.click(*constants.REPORT_VIEW_BATCH_TAB)
    pyautogui.write("unnamed")
    pyautogui.press("enter")
    
    pyautogui.click(*constants.REPORT_VIEW_SPEC_SELECT)
    pyautogui.write(str(specimen_ID))
    pyautogui.press("enter")
    
    pyautogui.click(*constants.REPORT_VIEW_LOAD_BTN)
    time.sleep(0.1)
    pyautogui.click(*constants.REPORT_VIEW_EXPORT_CSV_BTN)
    
    pyautogui.click(*constants.REPORT_VIEW_EXPORT_CHANNEL_SELECT_ALL_BTN)
    pyautogui.click(*constants.REPORT_VIEW_FINAL_EXPORT_CSV_BTN)
    
    # Press select folder button
    pyautogui.click(*constants.REPORT_VIEW_SELECT_FOLDER_BTN)
    # press extract csv button
    pyautogui.click(*constants.REPORT_VIEW_COMPLETE_CSV_BTN)
    # press exit button
    pyautogui.click(*constants.REPORT_VIEW_EXIT_CSV_BTN)
    
    csv_path =  constants.CSV_REPORT_FOLDER / f"{specimen_ID}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file was not created: {csv_path}"
        )

    return str(csv_path)