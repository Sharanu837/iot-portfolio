import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Face Detection Setup
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

face_detection = mp_face.FaceDetection(min_detection_confidence=0.6)

# Windows DirectShow Camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Flip for Selfie Mirror View
    display_frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = display_frame.shape

    # RGB Conversion
    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_frame)

    if results.detections:
        for detection in results.detections:
            # Bounding Box Coordinates
            bboxC = detection.location_data.relative_bounding_box
            x = int(bboxC.xmin * frame_w)
            y = int(bboxC.ymin * frame_h)
            w = int(bboxC.width * frame_w)
            h = int(bboxC.height * frame_h)

            # Ensure coordinates stay inside frame boundary
            x, y = max(0, x), max(0, y)
            w, h = min(frame_w - x, w), min(frame_h - y, h)

            # Lower Face Region ROI (Nose & Mouth Region)
            lower_face_y = y + int(h * 0.5)
            lower_face_h = int(h * 0.5)
            
            lower_face_roi = display_frame[lower_face_y : lower_face_y + lower_face_h, x : x + w]

            # Mask Detection Logic using Variance/Edge/Color Density
            label = "Detecting..."
            color = (255, 255, 255)

            if lower_face_roi.size != 0:
                # Convert ROI to HSV color space
                hsv_roi = cv2.cvtColor(lower_face_roi, cv2.COLOR_BGR2HSV)
                
                # Check Skin Color Density in lower face
                # Typical skin color HSV bounds
                lower_skin = np.array([0, 20, 70], dtype=np.uint8)
                upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                
                skin_mask = cv2.inRange(hsv_roi, lower_skin, upper_skin)
                skin_ratio = (cv2.countNonZero(skin_mask) / (w * lower_face_h)) * 100

                # Agar lower face par skin percentage kam hai -> Mask Detected
                if skin_ratio < 18.0:
                    label = "Mask Detected"
                    color = (0, 255, 0)  # Green Box
                else:
                    label = "No Mask"
                    color = (0, 0, 255)  # Red Box

            # Draw Bounding Box and Label
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(display_frame, (x, y - 35), (x + w, y), color, cv2.FILLED)
            cv2.putText(display_frame, label, (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Face Mask Detection", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
