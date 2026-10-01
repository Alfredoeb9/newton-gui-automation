import asyncio
import time
import ocr.ocr as ocr

latest_data = {}

async def update_newton_data():

    global latest_data

    while True:

        try:
            start = time.perf_counter()
            
            latest_data = ocr.read_newton_values("all")
            
            elapsed = time.perf_counter() - start
            
            latest_data["server_time"] = time.time()
            
            print("Latest data:", latest_data)

        except Exception as e:
            print(f"OCR error: {e}")

        await asyncio.sleep(0.25)
