from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Literal
from fastapi import Query
from pydantic import BaseModel

import asyncio
from ocr.OCR_background import update_newton_data
import ocr.OCR_background as OCR_background
import helper_func
import newton_gui
import ocr.ocr as ocr
from constants import ( MAX_JOG_SECONDS )

helper_func.require_admin()

ocr_task = None
active_connections = 0

app = FastAPI(
    title = "Newton GUI API",
    description = "API wrapper for Newton GUI automation"
)

class TestSelection(BaseModel):
    name: str
    
# GET API to get current health and vitals of software and hardware
@app.get("/health")
def health():
    newton_running = newton_gui.is_newton_running()
    helper_func.activate_newton()
    
    if not newton_running:
        return {
            "status": "unhealthy",
            "api": {
                "connected": True
            },
            "newton": {
                "running": False
            },
            "hardware": {
                "connected": False,
                "ready": False
            }
        }

    return {
        "status": "healthy",
        "api": {
            "connected": True
        },
        "newton": {
            "running": True
        },
        "hardware": {
            "connected": None,
            "ready": None
        }
    }

# GET API to send user list of test filters
@app.get(
    "/tests",
    summary="Get a List of Filter Tests",
    description=(
        """Gets all created filter tests in which you can then use the /tests/select to prepare this test to run"""
    )
)
def get_tests():
    return newton_gui.get_filters()

# POST API to paste selected test filter
@app.post(
    "/tests/select",
    summary="Select a Newton test",
    description=(
        """Selects a test configuration from the available Newton test filters
        and enters the selected test name into the Online test filter field."""
    )
)
def select_test(selection: TestSelection):
    
    helper_func.require_newton_running()
    helper_func.activate_newton()

    filters = newton_gui.get_filters()

    selected_filter = next(
        (
            test
            for test in filters
            if test["name"] == selection.name
        ),
        None
    )

    if selected_filter is None:
        raise HTTPException(
            status_code=404,
            detail=f"Test not found: {selection.name}"
        )
        
    try:
        newton_gui.set_filter_online_tab(
            selected_filter["name"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to select test: {e}"
        )

    return {
        "status": "selected",
        "test": selected_filter
    }
    
@app.post("/tests/configure_specimen")
def configure_specimen(specimen_id: str, specimen_width: int, specimen_depth: int):
    helper_func.require_newton_running()
    
    try:
        newton_gui.configure_specimen(specimen_id, specimen_width, specimen_depth)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure speciment: {e}"
        )
        
    return {
        "status": "complete",
        "specimen": {
            "id": specimen_id,
            "width": specimen_width,
            "depth": specimen_depth
        }
    }    


# POST API to start test
@app.post("/tests/start")
def start_test():

    helper_func.require_newton_running()
    helper_func.activate_newton()

    try:
        newton_gui.start_test()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start test: {e}"
        )

    return {
        "status": "started"
    }

# POST API to stop current test running
@app.post("/tests/stop")
def stop_test():
    helper_func.require_newton_running()
    helper_func.activate_newton()

    try:
        newton_gui.stop_test()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop test: {e}"
        )
    return {
        "status": "stopped"
    }

# POST API to pause running test
@app.post("/tests/pause")
def pause_test():
    helper_func.require_newton_running()
    helper_func.activate_newton()

    try:
        newton_gui.pause_resume_btn()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pause test: {e}"
        )
        
    return {
        "status": "pause clicked"
    }
    
# POST API to resume running test
@app.post("/tests/resume")
def resume_test():
    helper_func.require_newton_running()
    helper_func.activate_newton()

    try:
        newton_gui.pause_resume_btn()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume test: {e}"
        )
        
    return {
        "status": "resume clicked"
    }

# POST API to run jog up high button
@app.post("/jog/up/fast")
def jog_up_fast(seconds: float = 1):
    
    helper_func.require_newton_running()
    
    if seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="seconds must be greater than 0"
        )
        
    if seconds > MAX_JOG_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"seconds cannot exceed {MAX_JOG_SECONDS}"
        )
        
    try:
        newton_gui.jog_up_fast(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog up high: {e}"
        )

    return {
        "status": "jogged up high",
        "seconds": seconds
    }
    
# POST API to run jog up high button
@app.post("/jog/up/slow")
def jog_up_slow(seconds: float = 1):
    
    helper_func.require_newton_running()
    
    if seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="seconds must be greater than 0"
        )
        
    if seconds > MAX_JOG_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"seconds cannot exceed {MAX_JOG_SECONDS}"
        )
        
    try:
        newton_gui.jog_up_slow(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog up low: {e}"
        )

    return {
        "status": "jogged up low",
        "seconds": seconds
    }

# POST API to run jog down high button
@app.post("/jog/down/fast")
def jog_down_fast(seconds: float = 1):
    
    helper_func.require_newton_running()
    
    if seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="seconds must be greater than 0"
        )

    try:
        newton_gui.jog_down_fast(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog down high: {e}"
        )
        
    return {
        "status": "jogged down fast",
        "seconds": seconds
    }
    
    # POST API to run jog down high button
@app.post("/jog/down/slow")
def jog_down_slow(seconds: float = 1):
    
    helper_func.require_newton_running()
    
    if seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="seconds must be greater than 0"
        )

    try:
        newton_gui.jog_down_slow(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog down low: {e}"
        )
        
    return {
        "status": "jogged down slow",
        "seconds": seconds
    }
    
@app.get(
    "/data",
    summary="Read Newton test data",
    description=(
        """Reads live values from the Newton GUI using OCR.
         
        Query must be one of: 'all', 'rate', or 'max'."""
    )
)
def get_data(
    query: Literal["all", "max", "rate"] = Query(
        description=(
            """Select the Newton data to retrieve. \n
            'all' = current, rate, and maximum values. \n
            'rate' = strain, position, and load rates. \n
            'max' = maximum strain, position, and load values."""
        )
    )
):
    
    helper_func.require_newton_running()
    
    try:
        data = ocr.read_newton_values(query)
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read Newton data: {e}"
        )
        
    return {
        "status": "success",
        "data": data
    }
    
@app.post("/report/download")
def download_report(batchID: str):
    helper_func.require_newton_running()
    
    try:
        report = newton_gui.download_report(batchID)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download Newton report: {e}"
        )
        
    return {
        "status": "success",
        "sent_to": report
    }
    
@app.post("/report/extract_csv")
def extract_csv(specimen_ID: str):
    helper_func.require_newton_running()
        
    try:
        report = newton_gui.download_report(specimen_ID)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download Newton report: {e}"
        )
        
    return {
        "status": "success",
        "sent_to": report
    }
        
    
# Websocket to listen to S:Strain Ch:Position Ch:Load values
# Approx ~0.25 - 0.5+ seconds for each run
@app.websocket("/ws/data")
async def websocket_data(websocket: WebSocket):

    global ocr_task
    global active_connections

    await websocket.accept()

    active_connections += 1

    print(
        f"Client connected. "
        f"Active connections: {active_connections}"
    )

    # Start OCR if this is the first client
    if ocr_task is None or ocr_task.done():

        print("Starting OCR background task...")

        ocr_task = asyncio.create_task(
            OCR_background.update_newton_data()
        )

    try:

        while True:

            await websocket.send_json(
                OCR_background.latest_data
            )

            await asyncio.sleep(0.25)

    except WebSocketDisconnect:

        print("Client disconnected")
    except asyncio.CancelledError:
        print("WebSocket task cancelled")

        raise
    finally:

        active_connections -= 1

        print(
            f"Active connections: {active_connections}"
        )

        # Stop OCR when nobody is listening
        if active_connections == 0:

            print("Stopping OCR background task...")

            if ocr_task is not None:

                ocr_task.cancel()

                ocr_task = None
                
@app.get("/live", response_class=HTMLResponse)
def live_page():

    return """
    <!DOCTYPE html>
    <html>

    <head>

        <title>Newton Live Data</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 40px;
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
            }

            .status {
                text-align: center;
                margin-bottom: 25px;
                font-weight: bold;
            }

            .data-container {
                max-width: 900px;
                margin: auto;

                display: grid;
                grid-template-columns:
                    repeat(3, 1fr);

                gap: 20px;
            }

            .card {
                background-color: white;
                padding: 25px;
                border-radius: 10px;

                box-shadow:
                    0 2px 8px
                    rgba(0, 0, 0, 0.15);

                text-align: center;
            }

            .label {
                font-size: 18px;
                color: #666;
                margin-bottom: 10px;
            }

            .value {
                font-size: 28px;
                font-weight: bold;
            }

            .rate {
                margin-top: 10px;
                color: #555;
            }

            .max {
                margin-top: 10px;
                color: #777;
            }

        </style>

    </head>

    <body>

        <h1>Newton Live Data</h1>

        <div id="status" class="status">
            Connecting...
        </div>

        <div class="data-container">

            <div class="card">

                <div class="label">
                    Strain
                </div>

                <div id="strain" class="value">
                    --
                </div>

                <div class="rate">
                    Rate:
                    <span id="strain_rate">
                        --
                    </span>
                </div>

                <div class="max">
                    Max:
                    <span id="strain_max">
                        --
                    </span>
                </div>

            </div>


            <div class="card">

                <div class="label">
                    Position
                </div>

                <div id="position" class="value">
                    --
                </div>

                <div class="rate">
                    Rate:
                    <span id="position_rate">
                        --
                    </span>
                </div>

                <div class="max">
                    Max:
                    <span id="position_max">
                        --
                    </span>
                </div>

            </div>


            <div class="card">

                <div class="label">
                    Load
                </div>

                <div id="load" class="value">
                    --
                </div>

                <div class="rate">
                    Rate:
                    <span id="load_rate">
                        --
                    </span>
                </div>

                <div class="max">
                    Max:
                    <span id="load_max">
                        --
                    </span>
                </div>

            </div>

        </div>


        <script>
            const status = document.getElementById("status");

            const strain = document.getElementById("strain");

            const strainRate = document.getElementById("strain_rate");

            const strainMax = document.getElementById("strain_max");

            const position = document.getElementById("position");

            const positionRate = document.getElementById("position_rate");

            const positionMax = document.getElementById("position_max");

            const load = document.getElementById("load");

            const loadRate = document.getElementById("load_rate");

            const loadMax = document.getElementById("load_max");


            const protocol =
                window.location.protocol === "https:"
                    ? "wss:"
                    : "ws:";
                    
            const websocket =
                new WebSocket(
                    protocol +
                    "//" +
                    window.location.host +
                    "/ws/data"
                );

            websocket.onopen = function() {
                status.textContent = "Connected";
                status.style.color ="green";
            };

            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);                    

                strain.textContent = data.strain ?? "--";
                strainRate.textContent = data.strain_rate ?? "--";
                strainMax.textContent = data.strain_max ?? "--";

                position.textContent =data.position ?? "--";
                positionRate.textContent = data.position_rate ?? "--";
                positionMax.textContent = data.position_max ?? "--";


                load.textContent = data.load ?? "--";
                loadRate.textContent = data.load_rate ?? "--";
                loadMax.textContent = data.load_max ?? "--";

            };


            websocket.onclose = function() {
                status.textContent = "Disconnected";
                status.style.color = "red";
            };


            websocket.onerror = function() {
                status.textContent = "Connection error";
                status.style.color = "red";
            };
            
            

        </script>

    </body>

    </html>
    """