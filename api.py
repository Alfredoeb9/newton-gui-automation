from fastapi import FastAPI, HTTPException
from typing import Literal
from fastapi import Query
from pydantic import BaseModel

import helper_func
import newton_gui
import ocr
from constants import ( MAX_JOG_SECONDS )

helper_func.require_admin()

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
@app.get("/tests")
def get_tests():
    return newton_gui.get_filters()

# POST API to paste selected test filter
@app.post("/tests/select")
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
@app.post("/jog/up/high")
def jog_up(seconds: float = 1):
    
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
        newton_gui.jog_up_high(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog up high: {e}"
        )

    return {
        "status": "jogged up",
        "seconds": seconds
    }

# POST API to run jog down high button
@app.post("/jog/down/high")
def jog_down(seconds: float = 1):
    
    helper_func.require_newton_running()
    
    if seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="seconds must be greater than 0"
        )

    try:
        newton_gui.jog_down_high(seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to jog down high: {e}"
        )
        
    return {
        "status": "jogged down",
        "seconds": seconds
    }
    
@app.get('/data')
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