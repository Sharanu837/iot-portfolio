import cv2
import mediapipe as mp
import pyautogui
import math

# Screen size get karein
screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

# MediaPipe Setup
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

# Cursor smoothing variables
prev_x, prev_y = 0, 0
smoothening = 5

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Flip frame for selfie view
    display_frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = display_frame.shape

    # RGB Conversion
    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            
            # Index Finger Tip (Landmark 8) & Thumb Tip (Landmark 4)
            index_tip = landmarks[8]
            thumb_tip = landmarks[4]

            # Frame Pixel coordinates
            index_x = int(index_tip.x * frame_w)
            index_y = int(index_tip.y * frame_h)
            thumb_x = int(thumb_tip.x * frame_w)
            thumb_y = int(thumb_tip.y * frame_h)

            # Map to Screen Resolution
            target_x = int(index_tip.x * screen_width)
            target_y = int(index_tip.y * screen_height)

            # Smooth Movement
            curr_x = prev_x + (target_x - prev_x) / smoothening
            curr_y = prev_y + (target_y - prev_y) / smoothening

            # Move Mouse Cursor
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Visual Dot on Index Tip
            cv2.circle(display_frame, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)

            # Calculate Distance for Pinch Gesture
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            # Pinch detected -> Left Click
            if distance < 30:
                cv2.circle(display_frame, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                pyautogui.sleep(0.1)  # Brief pause to avoid accidental double clicks

    cv2.imshow("Virtual Mouse", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
