import pytesseract
import pyautogui
import data_logger
from PIL import Image
import constants
from helper_func import activate_newton

# tessearact executable file
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# track the values wanted
def capture_value(top_left: tuple[int, int], bottom_right: tuple[int, int]) -> Image:
    left, top = top_left
    right, bottom = bottom_right

    width = right - left
    height = bottom - top

    return pyautogui.screenshot(
        region=(left, top, width, height)
    )

# Extract the values in the screenshot as string
def read_value(top_left: tuple[int, int], bottom_right: tuple[int, int]) -> str:
    screenshot = capture_value(
        top_left,
        bottom_right
    )

    return pytesseract.image_to_string(
        screenshot,
        config="--psm 7 -c tessedit_char_whitelist=0123456789.-"
    ).strip()
    
# Main action to capture screenshot and read values from screenshot
def read_newton_values() -> dict[str, str]:
    activate_newton()
    
    strain = read_value(
        constants.ONLINE_STRAIN_VALUE_TOP_LEFT,
        constants.ONLINE_STRAIN_VALUE_BOTTOM_RIGHT
    )
    
    strain_rate = read_value(
        constants.ONLINE_STRAIN_RATE_VALUE_TOP_LEFT,
        constants.ONLINE_STRAIN_RATE_VALUE_BOTTOM_RIGHT
    )

    position = read_value(
        constants.ONLINE_POS_VALUE_TOP_LEFT,
        constants.ONLINE_POS_VALUE_BOTTOM_RIGHT
    )
    
    position_rate = read_value(
        constants.ONLINE_POS_RATE_VALUE_TOP_LEFT,
        constants.ONLINE_POS_RATE_VALUE_BOTTOM_RIGHT
    )

    load = read_value(
        constants.ONLINE_LOAD_VALUE_TOP_LEFT,
        constants.ONLINE_LOAD_VALUE_BOTTOM_RIGHT
    )
    
    load_rate = read_value(
        constants.ONLINE_LOAD_RATE_VALUE_TOP_LEFT,
        constants.ONLINE_LOAD_RATE_VALUE_BOTTOM_RIGHT
    )
    
    values = {
        "strain": strain,
        "strain_rate": strain_rate,
        "position": position,
        "position_rate": position_rate,
        "load": load,
        "load_rate": load_rate
    }
    
    # Check for empty OCR values
    missing_values = []
    
    for name, value in values.items():
        if not value:
            missing_values.append(name)
            
    if len(missing_values) > 0:
        raise RuntimeError(f"OCR failed to read: {', '.join(missing_values)}")
    
    # Formatted data to send to use
    data = {
        "strain": strain + " in",
        "strain_rate": strain_rate + " in/min",
        "position": position + " mm",
        "position_rate": position_rate + " mm/min",
        "load": load + " N",
        "load_rate": load_rate + " N/min"
    }
    
    # Save the txt file into a logger file (Desktop/Newton/Online_Values/newton_data.txt)
    data_logger.save_reading(data)

    return data

# If we need to run this file separately
if __name__ == "__main__":

    values = read_newton_values()

    print("Strain:", values["strain"])
    print("Strain_rate:", values["strain_rate"])
    print("Position:", values["position"])
    print("Position_rate:", values["position_rate"])
    print("Load:", values["load"])
    print("Load_rate:", values["load_rate"])