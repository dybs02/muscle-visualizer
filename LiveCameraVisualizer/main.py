import time
import cv2
import numpy as np
import serial

FRAME_HEIGHT = None
FRAME_WIDTH = None
ARDUINO_PORT = 'COM12'
ARDUINO = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=.1)
time.sleep(2)  # Allow time for Arduino to reset

def load_image(image_path, target_height, target_width):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel if available
    if image is None:
        print(f"Error: Could not read image {image_path}")
        exit(-1)

    resized_image = cv2.resize(image, (target_width, target_height))
    return resized_image

def blend_image(frame, overlay, x_offset, y_offset, alpha_overlay):
    """Blend overlay image onto the frame at specified offset with transparency."""
    y1, y2 = y_offset, y_offset + overlay.shape[0]
    x1, x2 = x_offset, x_offset + overlay.shape[1]

    alpha_s = (overlay[:, :, 3] / 255.0) * alpha_overlay  # Extract alpha channel and scale by alpha_overlay
    alpha_l = 1.0 - alpha_s

    for c in range(3):  # Blend RGB channels
        frame[y1:y2, x1:x2, c] = (
            alpha_s * overlay[:, :, c] + alpha_l * frame[y1:y2, x1:x2, c]
        )

def set_camera_resolution(cap):
    # Query maximum resolution supported by the camera
    max_width = 1280
    max_height = 720

    # Set resolution to the maximum available
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, max_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, max_height)

    print(f"Camera resolution set to {max_width}x{max_height}")
    return max_width, max_height

def read_emg_value():
    try:
        if ARDUINO.in_waiting > 0:  # Check if data is available
            line = ARDUINO.readline().decode('utf-8').strip()  # Read line
            if line.isdigit():  # Ensure it's a valid number
                return int(line)
    except (ValueError, serial.SerialException):
        pass  # Ignore errors
    return 0  # Default if no valid data


def display_camera_with_images(camera_index):
    # cap = cv2.VideoCapture(camera_index)  
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW) #app lunches faster
    # cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Set the camera to maximum resolution
    max_width, max_height = set_camera_resolution(cap)

    ret, frame = cap.read()
    if not ret:
        exit(-1)

    global FRAME_HEIGHT, FRAME_WIDTH
    FRAME_HEIGHT = max_height
    FRAME_WIDTH = max_width

    # Load images with alpha channel and resize them
    image_left = load_image('./images/arm_left_idle4.png', FRAME_HEIGHT, int(FRAME_WIDTH / 6))
    image_right = load_image('./images/arm_right_idle4.png', FRAME_HEIGHT, int(FRAME_WIDTH / 6))
    image_left_active = load_image('./images/arm_left_active.png', FRAME_HEIGHT, int(FRAME_WIDTH / 6))
    image_right_active = load_image('./images/arm_right_active.png', FRAME_HEIGHT, int(FRAME_WIDTH / 6))
    ARDUINO.flushInput()  # Clear any garbage data

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Can't receive frame. Exiting ...")
            break

        # Read sensor value (mocked for now as Arduino communication might not work here)
        emg_value = read_emg_value()


        print(f"EMG Value: {emg_value}")

        # Normalize EMG value to transparency (0 to 1)
        alpha = max(0, min(1, emg_value / 1000))

        # Blend idle images on the frame
        blend_image(frame, image_left, 0, 0, 1.0)  # Fully visible idle left image
        blend_image(frame, image_right, FRAME_WIDTH - image_right.shape[1], 0, 1.0)  # Fully visible idle right image

        # Blend active images on the frame with transparency based on EMG value
        blend_image(frame, image_left_active, 0, 0, alpha)
        blend_image(frame, image_right_active, FRAME_WIDTH - image_right_active.shape[1], 0, alpha)

        # Display the combined frame
        cv2.imshow('Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Pass the desired camera index (0 for primary, 1 for secondary, etc.)
    display_camera_with_images(camera_index=1)
