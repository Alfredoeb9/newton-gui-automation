import time
import threading

import cv2
from pygrabber.dshow_graph import FilterGraph


graph = None

camera_lock = threading.Lock()
camera_running = False

latest_frame = None
frame_lock = threading.Lock()

viewer_count = 0
viewer_lock = threading.Lock()


def on_frame(frame):
    global latest_frame

    with frame_lock:
        latest_frame = frame.copy()


def start_camera():
    global graph
    global camera_running
    global latest_frame

    with camera_lock:
        # Camera is already running
        if camera_running:
            return

        print("Starting camera...")

        # Clear previous frame
        with frame_lock:
            latest_frame = None

        # Create DirectShow graph
        graph = FilterGraph()

        # Find cameras
        devices = graph.get_input_devices()

        print("Cameras:")

        for index, device in enumerate(devices):
            print(f"{index}: {device}")

        if not devices:
            raise RuntimeError("No cameras found")

        camera_index = 0

        print(f"\nOpening: {devices[camera_index]}")

        # Add camera
        graph.add_video_input_device(camera_index)

        # Add sample grabber
        graph.add_sample_grabber(on_frame)

        # No DirectShow preview window
        graph.add_null_render()

        # Connect graph
        graph.prepare_preview_graph()

        # Start camera
        graph.run()

        camera_running = True

        print("Camera is running.")

        # Start ONE camera loop
        thread = threading.Thread(target=camera_loop, daemon=True)

        thread.start()


def stop_camera():
    global graph
    global camera_running

    with camera_lock:
        if not camera_running:
            return

        print("Stopping camera...")

        # Tell camera loop to stop
        camera_running = False

        try:
            if graph is not None:
                graph.stop()

        except Exception as e:
            print(f"Camera stop error: {e}")

        graph = None

        print("Camera stopped.")


def camera_loop():
    print("Camera loop started.")

    while camera_running:
        try:
            # Request next frame
            graph.grab_frame()

        except Exception as e:
            print(f"Camera error: {e}")
            break

        time.sleep(0.01)

    print("Camera loop stopped.")


def add_viewer():
    global viewer_count

    with viewer_lock:
        viewer_count += 1
        print(f"Viewer connected. Viewers: {viewer_count}")

        # First viewer starts camera
        if viewer_count == 1:
            start_camera()


def remove_viewer():
    global viewer_count

    with viewer_lock:
        viewer_count -= 1

        # Safety
        if viewer_count < 0:
            viewer_count = 0

        print(f"Viewer disconnected. Viewers: {viewer_count}")

        # Last viewer disconnected
        if viewer_count == 0:
            stop_camera()


def generate_frames():
    add_viewer()

    try:
        while True:
            # Get most recent camera frame
            with frame_lock:
                if latest_frame is None:
                    frame = None
                else:
                    frame = latest_frame.copy()

            # Camera hasn't produced a frame yet
            if frame is None:
                time.sleep(0.01)
                continue

            # Convert to JPEG
            success, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

            if not success:
                continue

            # Send MJPEG frame across HTTP
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + jpeg.tobytes()
                + b"\r\n"
            )

            time.sleep(0.03)

    finally:
        remove_viewer()