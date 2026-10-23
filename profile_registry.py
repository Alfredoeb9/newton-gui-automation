import json
import difflib
import re
import time
from PIL import Image, ImageOps
import pyautogui
import pytesseract
import constants
# import helper_func
# from helper_func import activate_newton, activate_tab
from helper_func import clear_input_field
import newton_gui
from ocr.ocr import capture_value

PART_RE = re.compile(r"^(?P<base>.+)_part_(?P<num>\d+)$", re.IGNORECASE)

def search_profile(profile_name: str) -> dict:
    pyautogui.click(constants.TEST_SEARCH_BAR)
    pyautogui.write(profile_name)
    
def read_test_list(top_left, bottom_right) -> list[dict]:
    img = capture_value(top_left, bottom_right)
    img = ImageOps.grayscale(img)
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.point(lambda p: 0 if p < 170 else 255)

    data = pytesseract.image_to_data(img, config="--psm 6", output_type=pytesseract.Output.DICT)

    # Group words into lines, keeping each line's on-screen y for clicking later
    lines: dict[tuple, dict] = {}
    
    for i, word in enumerate(data["text"]):
        
        if not word.strip():
            continue
        
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        line = lines.setdefault(key, {"words": [], "y": data["top"][i] + data["height"][i] // 2})
        line["words"].append(word)

    known = [f["name"] for f in newton_gui.get_filters()]
    
    results = []
    
    for line in lines.values():
        raw = " ".join(line["words"])
        match = difflib.get_close_matches(raw, known, n=1, cutoff=0.6)
        results.append({
            "name": match[0] if match else None,
            
        })
        
    return results
    

    

def read_text(top_left, bottom_right, numeric: bool) -> str:
    img = capture_value(top_left, bottom_right).convert("L")
    
    # Upscaling noticeably improves Tesseract accuracy on small GUI fonts
    img = img.resize((img.width * 3, img.height * 3))
    config = "--psm 7"
    
    if numeric:
        config += " -c tessedit_char_whitelist=0123456789.-"
        
    return pytesseract.image_to_string(img, config=config).strip()


def find_family(test_name: str) -> tuple[str, list[tuple[int, dict]]]:
    match = PART_RE.match(test_name)
    base = match["base"] if match else test_name
    
    parts = []
    
    for f in newton_gui.get_filters():
        m = PART_RE.match(f["name"])
        
        if m and m["base"].lower() == base.lower():
            parts.append((int(m["num"]), f))
            
    return base, sorted(parts, key=lambda p: p[0])

def read_ramp_settings() -> dict:
    ramp = {}

    for name, (top_left, bottom_right, numeric) in constants.RAMP_SETTINGS_FIELDS.items():
        raw = read_text(top_left, bottom_right, numeric)

        if name == "end_channel":
            normalized = raw.casefold().replace(" ", "")
            match = next(
                (
                    option
                    for option in constants.RAMP_END_CHANNEL_OPTIONS
                    if option.casefold().replace(" ", "") == normalized
                ),
                None,
            )
            ramp[name] = match
            if match is None:
                ramp.setdefault("ocr_errors", []).append(
                    f"{name}={raw!r}"
                )
        elif numeric:
            try:
                ramp[name] = float(raw)
            except ValueError:
                ramp[name] = None
                ramp.setdefault("ocr_errors", []).append(f"{name}={raw!r}")
        else:
            ramp[name] = raw or None

    return ramp

def read_fields(fields: dict) -> dict:
    result = {}

    for name, (top_left, bottom_right, numeric) in fields.items():
        raw = read_text(top_left, bottom_right, numeric)

        if name == "end_channel":
            normalized = raw.casefold().replace(" ", "")
            value = next(
                (
                    option
                    for option in constants.RAMP_END_CHANNEL_OPTIONS
                    if option.casefold().replace(" ", "") == normalized
                ),
                None,
            )
        elif numeric:
            try:
                value = float(raw)
            except ValueError:
                value = None
        else:
            value = raw or None

        result[name] = value

        if value is None:
            result.setdefault("ocr_errors", []).append(f"{name}={raw!r}")

    return result



def read_segment(segment_number: int) -> dict:
    pyautogui.click(constants.TEST_EDIT_BUTTON)
    pyautogui.click(constants.TEST_NEXT_BUTTON)
    pyautogui.click(constants.TEST_SEG_EDIT_BUTTON)
    
    segment = {"index": segment_number}
    segment.update(read_fields(constants.PROFILE_SEGMENT_PRECOND_FIELDS))
    
    segment["channels"] = {}
            
    pyautogui.click(constants.TEST_CHANNEL_BTN)
            
    # Control Settings Box
    for channel_index, (name, (tl, br, numeric)) in enumerate(constants.PROFILE_SEGMENT_CONTROL_FIELDS.items(),start=1,):
        clear_input_field(constants.TEST_CHANNEL_CONTROL_DROP_DOWN[0], constants.TEST_CHANNEL_CONTROL_DROP_DOWN[1], "")

        if (channel_index == 1):
            pyautogui.write("Position")
            pyautogui.press("enter")
        elif (channel_index == 2):
            pyautogui.write("Load")
            pyautogui.press("enter")
        elif (channel_index == 3):
            pyautogui.write("Stress")
            pyautogui.press("enter")
        elif (channel_index == 4):
            pyautogui.write("Strain")
            pyautogui.press("enter")
            
        raw = read_text(tl, br, numeric)
        
        if numeric:
            try:
                segment[name] = float(raw)
            except ValueError:
                segment[name] = None
                segment.setdefault("ocr_errors", []).append(f"{name}={raw!r}")
        else:
            segment[name] = raw or None
            
    # Profile Settings Box
    for profile_index, profile_name in enumerate(constants.RAMP_PROFILE_NAMES, start=1):
        pyautogui.click(constants.TEST_CHANNEL_PROFILE_SET_BTN)
        pyautogui.write(profile_name)
        pyautogui.press("enter")
        
        
        raw = read_text(*constants.PROFILE_SEGMENT_PROFILE_FIELDS["rate"])
        
        numeric = constants.PROFILE_SEGMENT_PROFILE_FIELDS["rate"][2]
        if numeric:
            try:
                segment[profile_name] = float(raw)
            except ValueError:
                segment[profile_name] = None
                segment.setdefault("ocr_errors", []).append(f"{profile_name}={raw!r}")
        else:
            segment[profile_name] = raw or None
            
        # Read the rate once for Up Ramp and Down Ramp 
        # For each Up and Down Ramp there are a set of 8 fields to read
        if (profile_name == "Up Ramp") or (profile_name == "Down Ramp"):
            for field_index, end_channel_option in enumerate(constants.RAMP_END_CHANNEL_OPTIONS, start=1):
                pyautogui.click(constants.TEST_CHANNEL_END_CHANNEL_INPUT)
                clear_input_field(constants.TEST_CHANNEL_END_CHANNEL_INPUT[0], constants.TEST_CHANNEL_END_CHANNEL_INPUT[1],"")
                
                pyautogui.write(str(end_channel_option))
                pyautogui.press("enter")
                
                raw = read_text(*constants.RAMP_SETTINGS_FIELDS["end_value"])
            
                numeric = constants.RAMP_SETTINGS_FIELDS["end_value"][2]
                if numeric:
                    try:
                        segment[end_channel_option] = float(raw)
                    except ValueError:
                        segment[end_channel_option] = None
                        segment.setdefault("ocr_errors", []).append(f"{end_channel_option}={raw!r}")
                else:
                    segment[end_channel_option] = raw or None
    
    # Return back to available tests
    pyautogui.click(constants.TEST_MANAGEMENT_MAIN_TAB)
    pyautogui.click(constants.TEST_MANAGEMENT_TAB_CONFIRM)
    
    return segment


def read_profile(profile_name: str) -> list[dict]:
    search_profile(profile_name)
    
    return [read_segment(i) for i in range(len(constants.PROFILE_SEGMENT_TABS))]


def build_reg(test_name:str):
    # tests_available_for_segments = read_test_list(constants.TEST_LIST_TOP_LEFT, constants.TEST_LIST_BOTTOM_RIGHT)
    base, parts = find_family(test_name)
    
    profile = {}
    
    for i, (num, test) in enumerate(parts):
        # go into each profile and use ocr to capture its configuration and append to that object
        if test["name"]:
            segments = read_profile(test["name"])
            next_key = f"part_{parts[i + 1][0]}" if i + 1 < len(parts) else None
            profile[f"part_{num}"] = {
                "segments": segments,
                "allowed_next": [k for k in (next_key, "stop") if k],
            }
            test["segments"] = segments
    
    return profile

def build_registry(test_name: str) -> dict:
    base, parts = find_family(test_name)
    if not parts:
        raise ValueError(f"No profiles matching {base}_part_<n>")

    profiles = {}
    for i, (num, f) in enumerate(parts):
        segments = read_profile(f["name"])
        next_key = f"part_{parts[i + 1][0]}" if i + 1 < len(parts) else None
        profiles[f"part_{num}"] = {
            "file": f["file"],
            "mtime": (constants.NEWTON_TEST_DIR / f["file"]).stat().st_mtime,
            "segments": {
                "count": len(segments),
                "start": 1,
                "end": len(segments),
                "completion_condition": "all_axes",
                "details": segments,
            },
            "allowed_next": [k for k in (next_key, "stop") if k],
        }

    registry = {"test_name": base, "profiles": profiles}
    
    constants.PROFILE_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    
    path = constants.PROFILE_REGISTRY_DIR / f"{base}.json"
    path.write_text(json.dumps(registry, indent=2))
    
    return registry


def get_registry(test_name: str) -> dict:
    base, parts = find_family(test_name)
    path = constants.PROFILE_REGISTRY_DIR / f"{base}.json"
    
    if path.exists():
        cached = json.loads(path.read_text())
        
        fresh = all(
            cached["profiles"].get(f"part_{n}", {}).get("mtime")
            == (constants.NEWTON_TEST_DIR / f["file"]).stat().st_mtime
            for n, f in parts
        )
        
        if fresh:
            return cached
        
    return build_registry(test_name)

print(read_test_list(constants.TEST_AVAILABLE_TL, constants.TEST_AVAILABLE_BR))