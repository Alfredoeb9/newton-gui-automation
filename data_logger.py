from datetime import datetime
from pathlib import Path

LOG_DIR = Path(
    r"C:\Users\TRI Test Machine\Desktop\Newton Reports\Online_Values"
)

LOG_FILE = LOG_DIR / "newton_data.txt"

def save_reading(values: dict) -> None:
    
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as file:

        file.write(f"Timestamp: {timestamp}\n")
        file.write(f"Strain: {values['strain']}\n")
        file.write(f"Position: {values['position']}\n")
        file.write(f"Load: {values['load']}\n")
        file.write("-" * 40 + "\n")