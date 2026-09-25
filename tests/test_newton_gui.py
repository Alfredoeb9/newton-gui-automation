from unittest.mock import MagicMock, patch
import newton_gui

#TODO: Move the activate_newton() to one function to activate the window once
# then run all the tests

# IMPORTANT: When creating new test for APIs that talk to the newton make sure you use patch to mock
# so we dont actually run the hardware 

def test_newton_is_running():
    process = MagicMock()
    process.info = {"name": "Newton.exe"}

    with patch("newton_gui.psutil.process_iter") as mock_process_iter:
        mock_process_iter.return_value = [process]

        assert newton_gui.is_newton_running() is True
        
def test_newton_is_not_running():
    process = MagicMock()
    process.info = {"name": "notepad.exe"}

    with patch("newton_gui.psutil.process_iter") as mock_process_iter:
        mock_process_iter.return_value = [process]

        assert newton_gui.is_newton_running() is False
        
def test_start_btn():
    
    with patch("newton_gui.pyautogui") as mock_pyautogui:

        newton_gui.start_test()

        mock_pyautogui.click.assert_called_once_with(
            *newton_gui.constants.ONLINE_START_STOP_BTN
        )

def test_jog_up_high():
    
    with patch("newton_gui.pyautogui") as mock_pyautogui:
        with patch("newton_gui.time.sleep"):

            newton_gui.jog_up_high(2)

            mock_pyautogui.moveTo.assert_called_once_with(1530, 603)

            mock_pyautogui.mouseDown.assert_called_once_with(
                button="left"
            )

            mock_pyautogui.mouseUp.assert_called_once_with(
                button="left"
            )
            
def test_jog_up_releases_mouse_on_error():
    
    with patch("newton_gui.helper_func.activate_newton"):
        with patch("newton_gui.helper_func.activate_tab"):

            with patch("newton_gui.pyautogui") as mock_pyautogui:

                with patch(
                    "newton_gui.time.sleep",
                    side_effect=RuntimeError("test error")
                ):

                    try:
                        newton_gui.jog_up_high(2)
                    except RuntimeError:
                        pass

                    mock_pyautogui.mouseUp.assert_called_once_with(
                        button="left"
                    )
            
def test_jog_down_high():
    
    with patch("newton_gui.pyautogui") as mock_pyautogui:
        with patch("newton_gui.time.sleep"):
        
            newton_gui.jog_down_high(2)

            mock_pyautogui.moveTo.assert_called_once_with(1528, 818)

            mock_pyautogui.mouseDown.assert_called_once_with(
                button="left"
            )

            mock_pyautogui.mouseUp.assert_called_once_with(
                button="left"
            )

def test_jog_down_releases_mouse_on_error():
    with patch("newton_gui.helper_func.activate_newton"):
        with patch("newton_gui.helper_func.activate_tab"):

            with patch("newton_gui.pyautogui") as mock_pyautogui:

                with patch(
                    "newton_gui.time.sleep",
                    side_effect=RuntimeError("test error")
                ):

                    try:
                        newton_gui.jog_down_high(2)
                    except RuntimeError:
                        pass

                    mock_pyautogui.mouseUp.assert_called_once_with(
                        button="left"
                    )