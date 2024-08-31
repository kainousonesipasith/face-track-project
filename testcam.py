import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture.")
else:
    print("Video capture opened successfully.")

cap.release()
