import cv2
import mediapipe as mp
import random
import time

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

tip_ids = [4, 8, 12, 16, 20]
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

player_score = 0
computer_score = 0
computer_choice = "None"
result_text = "Show Gesture & Press 's' to play"

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    display_frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = display_frame.shape

    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    user_gesture = "Unknown"
    lm_list = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * frame_w), int(lm.y * frame_h)
                lm_list.append([id, cx, cy])

    if len(lm_list) != 0:
        fingers = []

        # Thumb
        if lm_list[tip_ids[0]][1] < lm_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        total_fingers = fingers.count(1)

        # Gesture Detection Logic
        if total_fingers == 0:
            user_gesture = "Rock"
        elif total_fingers == 5:
            user_gesture = "Paper"
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            user_gesture = "Scissors"

    # Screen Display UI
    cv2.rectangle(display_frame, (10, 10), (320, 140), (0, 0, 0), cv2.FILLED)
    cv2.putText(display_frame, f'Player: {user_gesture}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(display_frame, f'Computer: {computer_choice}', (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(display_frame, f'Score - You: {player_score} | CPU: {computer_score}', (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.putText(display_frame, result_text, (20, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Rock Paper Scissors", display_frame)

    key = cv2.waitKey(1) & 0xFF
    
    # Press 's' to start round
    if key == ord('s'):
        if user_gesture in ["Rock", "Paper", "Scissors"]:
            computer_choice = random.choice(["Rock", "Paper", "Scissors"])

            # Game Rules
            if user_gesture == computer_choice:
                result_text = "It's a Tie!"
            elif (user_gesture == "Rock" and computer_choice == "Scissors") or \
                 (user_gesture == "Paper" and computer_choice == "Rock") or \
                 (user_gesture == "Scissors" and computer_choice == "Paper"):
                result_text = "You Win!"
                player_score += 1
            else:
                result_text = "Computer Wins!"
                computer_score += 1
        else:
            result_text = "Show Rock, Paper or Scissors properly!"

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
