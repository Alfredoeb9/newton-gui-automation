from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from api import app
import newton_gui

# IMPORTANT: When creating new test for APIs that talk to the newton make sure you use patch to mock
# so we dont actually run the hardware 

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()
    
def test_get_filters():
    fake_tests = [
        Path("Flexure Strength Test-HT-600C.tst"),
        Path("Flexure Strength Test-HT-700C.tst"),
        Path("Tensile Test.tst"),
    ]

    with patch(
        "newton_gui.NEWTON_TEST_DIR"
    ) as mock_test_dir:

        mock_test_dir.glob.return_value = fake_tests

        filters = newton_gui.get_filters()

    assert filters == [
        {
            "name": "Flexure Strength Test-HT-600C",
            "file": "Flexure Strength Test-HT-600C.tst"
        },
        {
            "name": "Flexure Strength Test-HT-700C",
            "file": "Flexure Strength Test-HT-700C.tst"
        },
        {
            "name": "Tensile Test",
            "file": "Tensile Test.tst"
        }
    ]
    
def test_start_test():
    with patch("api.newton_gui.is_newton_running", return_value=True):
        with patch("api.newton_gui.start_test") as mock_start:

            response = client.post("/tests/start")

            assert response.status_code == 200
            assert response.json()["status"] == "started"

            mock_start.assert_called_once()
            
def test_start_test_when_newton_is_not_running():
    with patch(
        "api.newton_gui.is_newton_running",
        return_value=False
    ):

        response = client.post("/tests/start")

        assert response.status_code == 503
        
def test_select_nonexistent_test():
    with patch(
        "api.newton_gui.get_filters",
        return_value=[]
    ):

        response = client.post(
            "/tests/select",
            json={
                "name": "Does Not Exist"
            }
        )

        assert response.status_code == 404
        
def test_jog_up_rejects_long_duration():
    response = client.post(
        "/jog/up/high?seconds=100"
    )

    assert response.status_code == 400
    
def test_jog_up_rejects_zero():
    response = client.post(
        "/jog/up/high?seconds=0"
    )

    assert response.status_code == 400
    
def test_jog_up_rejects_negative():
    response = client.post(
        "/jog/up/high?seconds=-1"
    )

    assert response.status_code == 400