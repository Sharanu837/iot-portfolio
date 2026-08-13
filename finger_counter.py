import cv2

import mediapipe as mp



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



# IMPORTANT FIX: Windows ke liye DirectShow (CAP_DSHOW) use karein

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)



while cap.isOpened():

    success, frame = cap.read()

    if not success:

        print("Webcam feed nahi mil raha hai.")

        break



    # Selfie mirror view

    display_frame = cv2.flip(frame, 1)



    # Processing ke liye RGB

    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)



    lm_list = []

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            

            for id, lm in enumerate(hand_landmarks.landmark):

                h, w, c = display_frame.shape

                cx, cy = int(lm.x * w), int(lm.y * h)

                lm_list.append([id, cx, cy])



    # Finger Counting Logic

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



        cv2.rectangle(display_frame, (20, 20), (220, 100), (0, 0, 0), cv2.FILLED)

        cv2.putText(display_frame, f'Fingers: {total_fingers}', (30, 75), 

                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)



    cv2.imshow("Finger Counter", display_frame)



    if cv2.waitKey(1) & 0xFF == ord('q'):

        break



cap.release()

cv2.destroyAllWindows()
