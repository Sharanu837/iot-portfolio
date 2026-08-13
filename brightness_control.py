import cv2
import mediapipe as mp
import math
import numpy as np
import screen_brightness_control as sbc

# MediaPipe Hands Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# DirectShow for Windows Camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

brightBar = 400
brightPer = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Selfie Mirror view
    display_frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = display_frame.shape

    # RGB Conversion
    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    lm_list = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * frame_w), int(lm.y * frame_h)
                lm_list.append([id, cx, cy])

    if len(lm_list) != 0:
        # Index Tip = 8, Thumb Tip = 4
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        
        # Center point
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Visual indicators
        cv2.circle(display_frame, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(display_frame, (x2, y2), 10, (0, 255, 255), cv2.FILLED)
        cv2.line(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
        cv2.circle(display_frame, (cx, cy), 8, (0, 255, 255), cv2.FILLED)

        # Distance calculation
        length = math.hypot(x2 - x1, y2 - y1)

        # Map distance [20, 180] to Brightness [0, 100]
        brightPer = np.interp(length, [20, 180], [0, 100])
        brightBar = np.interp(length, [20, 180], [400, 150])

        # Set Screen Brightness
        try:
            sbc.set_brightness(int(brightPer))
        except Exception as e:
            pass

        if length < 20:
            cv2.circle(display_frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    # Brightness Bar UI Draw Karein
    cv2.rectangle(display_frame, (50, 150), (85, 400), (0, 255, 255), 3)
    cv2.rectangle(display_frame, (50, int(brightBar)), (85, 400), (0, 255, 255), cv2.FILLED)
    cv2.putText(display_frame, f'{int(brightPer)} %', (40, 450), 
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 3)

    cv2.imshow("Virtual Brightness Control", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
