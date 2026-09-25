import pytesseract
import pyautogui
import data_logger
from PIL import Image
import constants
from helper_func import activate_newton, buildDataObject

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
def read_newton_values(query: str | None = None) -> dict[str, str]:
    activate_newton()
    
    values = {}

    if query == "all":
        values["strain"] = read_value(
            constants.ONLINE_STRAIN_VALUE_TOP_LEFT,
            constants.ONLINE_STRAIN_VALUE_BOTTOM_RIGHT
        )

        values["strain_rate"] = read_value(
            constants.ONLINE_STRAIN_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_STRAIN_RATE_VALUE_BOTTOM_RIGHT
        )

        values["strain_max"] = read_value(
            constants.ONLINE_STRAIN_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_STRAIN_MAX_VALUE_BOTTOM_RIGHT
        )

        values["position"] = read_value(
            constants.ONLINE_POS_VALUE_TOP_LEFT,
            constants.ONLINE_POS_VALUE_BOTTOM_RIGHT
        )

        values["position_rate"] = read_value(
            constants.ONLINE_POS_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_POS_RATE_VALUE_BOTTOM_RIGHT
        )

        values["position_max"] = read_value(
            constants.ONLINE_POS_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_POS_MAX_VALUE_BOTTOM_RIGHT
        )

        values["load"] = read_value(
            constants.ONLINE_LOAD_VALUE_TOP_LEFT,
            constants.ONLINE_LOAD_VALUE_BOTTOM_RIGHT
        )

        values["load_rate"] = read_value(
            constants.ONLINE_LOAD_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_LOAD_RATE_VALUE_BOTTOM_RIGHT
        )

        values["load_max"] = read_value(
            constants.ONLINE_LOAD_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_LOAD_MAX_VALUE_BOTTOM_RIGHT
        )

    elif query == "rate":

        values["strain_rate"] = read_value(
            constants.ONLINE_STRAIN_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_STRAIN_RATE_VALUE_BOTTOM_RIGHT
        )

        values["position_rate"] = read_value(
            constants.ONLINE_POS_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_POS_RATE_VALUE_BOTTOM_RIGHT
        )

        values["load_rate"] = read_value(
            constants.ONLINE_LOAD_RATE_VALUE_TOP_LEFT,
            constants.ONLINE_LOAD_RATE_VALUE_BOTTOM_RIGHT
        )

    elif query == "max":

        values["strain_max"] = read_value(
            constants.ONLINE_STRAIN_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_STRAIN_MAX_VALUE_BOTTOM_RIGHT
        )

        values["position_max"] = read_value(
            constants.ONLINE_POS_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_POS_MAX_VALUE_BOTTOM_RIGHT
        )

        values["load_max"] = read_value(
            constants.ONLINE_LOAD_MAX_VALUE_TOP_LEFT,
            constants.ONLINE_LOAD_MAX_VALUE_BOTTOM_RIGHT
        )

    else:
        raise ValueError(
            "Invalid query. Use 'all', 'rate', or 'max'."
        )

    # Check for empty OCR values
    missing_values = []

    for name, value in values.items():

        if not value:
            missing_values.append(name)

    if len(missing_values) > 0:
        raise RuntimeError(
            f"OCR failed to read: {', '.join(missing_values)}"
        )
    
    data = buildDataObject(values)
    
    # Save the txt file into a logger file (Desktop/Newton/Online_Values/newton_data.txt)
    data_logger.save_reading(data, query)

    return data