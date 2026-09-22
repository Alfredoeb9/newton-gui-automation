from fastapi import HTTPException

import newton_gui

def require_newton_running():
    if not newton_gui.is_newton_running():
        raise HTTPException(
            status_code=503,
            detail="Newton.exe is not running"
        )