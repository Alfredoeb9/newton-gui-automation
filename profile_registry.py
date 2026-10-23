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
# from helper_func import clear_input_field
from helper_func import clear_input_field
import newton_gui
from ocr.ocr import capture_value

PART_RE = re.compile(r"^(?P<base>.+)_part_(?P<num>\d+)$", re.IGNORECASE)

def build_test_catalog() -> dict:
    profiles = {}
    families = {}

    for path in constants.NEWTON_TEST_DIR.glob("*.tst"):
        match = PART_RE.fullmatch(path.stem)

        profile = {
            "name": path.stem,
            "file": path.name,
            "family": match["base"] if match else None,
            "part_number": int(match["num"]) if match else None,
            "segments": None,
            "registered": False,
        }
        profiles[path.stem.casefold()] = profile

        if match:
            family_key = match["base"].casefold()
            family = families.setdefault(
                family_key,
                {"name": match["base"], "parts": {}},
            )
            family["parts"][int(match["num"])] = path.stem.casefold()

    for family in families.values():
        part_numbers = sorted(family["parts"])

        for index, part_number in enumerate(part_numbers):
            next_part = (
                f"part_{part_numbers[index + 1]}"
                if index + 1 < len(part_numbers)
                else None
            )
            profile_key = family["parts"][part_number]
            profiles[profile_key]["allowed_next"] = [
                item for item in (next_part, "stop") if item
            ]

        family["profiles"] = {
            f"part_{number}": profiles[family["parts"][number]]
            for number in part_numbers
        }
        del family["parts"]

    return {"profiles": profiles, "families": families}

def build_test_catalog_by_part() -> dict:
    grouped: dict[str, dict] = {}
    
    print("Test directory:", constants.NEWTON_TEST_DIR)
    print("Directory exists:", constants.NEWTON_TEST_DIR.exists())  

    for path in constants.NEWTON_TEST_DIR.glob("*.tst"):
        match = PART_RE.fullmatch(path.stem)
        
        print(
            f"file={path.name!r}, stem={path.stem!r}, "
            f"matches_part_pattern={bool(match)}"
        )
        if not match:
            continue

        base = match["base"]
        part_number = int(match["num"])
        family_key = base.casefold()

        family = grouped.setdefault(
            family_key,
            {
                "name": base,
                "parts": {},
            },
        )

        part_key = f"part_{part_number}"
        if part_key in family["parts"]:
            raise ValueError(
                f"Duplicate profile part {part_key!r} for family {base!r}"
            )

        family["parts"][part_number] = {
            "name": path.stem,
            "file": path.name,
            "segments": None,
            "registered": False,
        }

    families = {}

    for family_key, family in sorted(grouped.items()):
        part_numbers = sorted(family["parts"])
        profiles = {}

        for index, part_number in enumerate(part_numbers):
            profile = family["parts"][part_number]
            next_part = (
                f"part_{part_numbers[index + 1]}"
                if index + 1 < len(part_numbers)
                else None
            )

            profile["allowed_next"] = [
                option for option in (next_part, "stop") if option
            ]
            profiles[f"part_{part_number}"] = profile

        families[family_key] = {
            "name": family["name"],
            "profiles": profiles,
        }

    return {"families": families}

def search_profile(profile_name: str) -> dict:
    pyautogui.click(constants.TEST_SEARCH_BAR)
    pyautogui.write(profile_name)
    time.sleep(1)
    
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
        
    print(lines)
        
    return results
    
    
def build_visible_registry(search_name: str) -> dict:
    search_profile(search_name)

    visible_tests = read_test_list(constants.TEST_AVAILABLE_TL, constants.TEST_AVAILABLE_BR,)

    if not visible_tests:
        raise RuntimeError(
            f"No test profiles were recognized in the list for {search_name!r}"
        )

    registry = {"query": search_name, "profiles": {},}

    for test in visible_tests:
        profile_name = test["name"]

        # read_profile searches for this exact result before reading its segments.
        segments = read_profile(profile_name)

        registry["profiles"][profile_name.casefold()] = {
            "name": profile_name,
            "segments": segments,
            "registered": True,
        }

    return registry

    

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
    
    pyautogui.click(constants.TEST_FIRST_SELECTION)
    pyautogui.click(constants.TEST_EDIT_BUTTON)
    time.sleep(3)
    pyautogui.click(constants.TEST_NEXT_BUTTON)
    time.sleep(1)
    if segment_number == 0:
        pyautogui.click(constants.TEST_SEG_1)
    elif segment_number == 1:
        pyautogui.click(constants.TEST_SEG_2)
    time.sleep(1)
    pyautogui.click(constants.TEST_SEG_EDIT_BUTTON)
    time.sleep(1)
    
    segment = {"index": segment_number}
    segment.update(read_fields(constants.PROFILE_SEGMENT_PRECOND_FIELDS))
    
    segment["channels"] = {}
            
    pyautogui.click(constants.TEST_CHANNEL_BTN)
            
    # Control Settings Box
    for channel_index, name in enumerate(constants.PROFILE_CONTROL_CHANNELS):
        clear_input_field(constants.TEST_CHANNEL_CONTROL_DROP_DOWN[0], constants.TEST_CHANNEL_CONTROL_DROP_DOWN[1])

        # if (channel_index == 0):
        #     pyautogui.write("Position")
        #     pyautogui.press("enter")
        # elif (channel_index == 1):
        #     pyautogui.write("Load")
        #     pyautogui.press("enter")
        # elif (channel_index == 2):
        #     pyautogui.write("Stress")
        #     pyautogui.press("enter")
        # elif (channel_index == 3):
        #     pyautogui.write("Strain")
        #     pyautogui.press("enter")
        pyautogui.write(name)
        pyautogui.press("enter")
        # Loop through the three fields and read the text
        # PROFILE_SEGMENT_CONTROL_FIELDS = {
        #     "channel_proportional":    ((562, 348), (649, 375), False),
        #     "channel_integral":             ((718, 349), (806, 375), True),
        #     "channel_derivative":        ((1002, 346), (1216, 373), True)
        # }
        for attempt in range(3):
            raw = read_text(*constants.PROFILE_SEGMENT_CONTROL_FIELDS[name])
            if raw:
                break
            
            
        
        numeric = constants.PROFILE_SEGMENT_CONTROL_FIELDS[name][2]
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
        
        
        raw = read_text(*constants.PROFILE_SEGMENT_PROFILE_FIELDS["profile_rate"])
        
        numeric = constants.PROFILE_SEGMENT_PROFILE_FIELDS["profile_rate"][2]
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
            for field_index, end_channel_option in enumerate(constants.RAMP_END_CHANNEL_OPTIONS):
                pyautogui.click(constants.TEST_CHANNEL_END_CHANNEL_INPUT)
                clear_input_field(constants.TEST_CHANNEL_END_CHANNEL_INPUT[0], constants.TEST_CHANNEL_END_CHANNEL_INPUT[1])
                
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
    # pyautogui.click(constants.TEST_MANAGEMENT_MAIN_TAB)
    # pyautogui.click(constants.TEST_MANAGEMENT_TAB_CONFIRM)
    
    return segment

def read_profile(profile_name: str) -> list[dict]:
    # clear_input_field(constants.TEST_SEARCH_BAR[0], constants.TEST_SEARCH_BAR[1])
    # search_profile(profile_name)
    
    # return [
    #     read_segment(segment_number)
    #     for segment_number in range(len(constants.PROFILE_SEGMENT_TABS))
    # ]
    
    clear_input_field(*constants.TEST_SEARCH_BAR)
    search_profile(profile_name)

    segments = [read_segment(0)]

    pyautogui.click(*constants.TEST_BACK_BUTTON)
    time.sleep(2)
    pyautogui.click(*constants.TEST_NEXT_BUTTON)
    time.sleep(2)

    segments.append(read_segment(1))

    pyautogui.click(*constants.TEST_MANAGEMENT_MAIN_TAB)
    pyautogui.click(*constants.TEST_MANAGEMENT_TAB_CONFIRM)

    return segments
    
def register_profile(catalog: dict, profile_name: str) -> dict:
    time.sleep(4)
    profile_key = profile_name.casefold()
    profile = catalog["profiles"].get(profile_key)

    if profile is None:
        raise ValueError(f"Profile not found in catalog: {profile_name}")

    profile["segments"] = read_profile(profile["name"])
    profile["registered"] = True
    return profile


def build_reg(test_name:str):
    time.sleep(2)
    clear_input_field(constants.TEST_SEARCH_BAR[0], constants.TEST_SEARCH_BAR[1])
    search_profile(test_name)
    time.sleep(1)
    tests_available_for_segments = read_test_list(constants.TEST_AVAILABLE_TL, constants.TEST_AVAILABLE_BR)
    # base, parts = find_family(test_name)
    
    
    profile = {}
    
    for i, test in enumerate(tests_available_for_segments):
        print(test["name"])
        # go into each profile and use ocr to capture its configuration and append to that object
        if test["name"]:
            segments = read_profile(test["name"])
        #     next_key = f"part_{i + 1}" if i + 1 < len(tests_available_for_segments) else None
        #     profile[f"part_{i}"] = {
        #         "segments": segments,
        #         "allowed_next": [k for k in (next_key, "stop") if k],
        #     }
        #     test["segments"] = segments
    
    return profile

# print(build_reg("Flexure Strength Test-RT 20-40mm"))
registry = build_visible_registry("Flexure Strength Test-RT 20-40mm")
print(json.dumps(registry, indent=2))