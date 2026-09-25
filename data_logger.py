from datetime import datetime
from pathlib import Path

LOG_DIR = Path(
    r"C:\Users\TRI Test Machine\Desktop\Newton Reports\Online_Values"
)

LOG_FILE = LOG_DIR / "newton_data.txt"

def save_reading(values: dict, query: str) -> None:

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as file:

        file.write(f"Timestamp: {timestamp}\n")
        file.write(f"Query: {query}\n")

        for name, value in values.items():
            file.write(f"{name}: {value}\n")

        file.write("-" * 40 + "\n")