import time

import cv2
import numpy as np
import pandas as pd
import serial

FRAME_HEIGHT = None
ARDUINO_PORT = 'COM5'
ARDUINO = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=.1)


def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        exit(-1)

    aspect_ratio = image.shape[1] / image.shape[0]
    resized_tree = cv2.resize(image, (int(FRAME_HEIGHT * aspect_ratio), FRAME_HEIGHT))
    return resized_tree


def display_camera_with_image():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    ret, frame = cap.read()
    if not ret: exit(-1)
    
    global FRAME_HEIGHT
    FRAME_HEIGHT = frame.shape[0]


    # TODO better path
    image_blank = load_image('./images/blank.png')
    image_rear_deltoids = load_image('./images/rear_deltoids.png')

    if image_blank is None:
        print(f"Error: Could not read image")
        return

    while True:
        # time.sleep(0.05) 
        ret, frame = cap.read()

        if not ret:
            print("Error: Can't receive frame. Exiting ...")
            break

        emg_value = int(ARDUINO.readline().decode('utf-8'))
        print(emg_value)

        muscle_image = cv2.addWeighted(image_blank, 1, image_rear_deltoids, emg_value/1000, 0)
        combined_frame = np.hstack((frame, muscle_image))

        cv2.imshow('Camera Feed', combined_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    display_camera_with_image()
