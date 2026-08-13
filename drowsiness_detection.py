import cv2
import mediapipe as mp
import math
import time
import winsound  # Windows built-in sound function

# MediaPipe Face Mesh Setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Eye Landmark IDs (Left and Right Eyes)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def calculate_ear(landmarks, eye_points, frame_w, frame_h):
    # Eye landmarks pixel positions
    pts = []
    for idx in eye_points:
        lm = landmarks[idx]
        pts.append((int(lm.x * frame_w), int(lm.y * frame_h)))

    # Vertical Distances
    v1 = math.hypot(pts[1][0] - pts[5][0], pts[1][1] - pts[5][1])
    v2 = math.hypot(pts[2][0] - pts[4][0], pts[2][1] - pts[4][1])

    # Horizontal Distance
    h = math.hypot(pts[0][0] - pts[3][0], pts[0][1] - pts[3][1])

    # Eye Aspect Ratio (EAR)
    ear = (v1 + v2) / (2.0 * h)
    return ear

# Camera Setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

EAR_THRESHOLD = 0.22    # EAR threshold (Eyes Closed)
CLOSED_TIME_LIMIT = 2.0  # Seconds before Alarm triggers

eyes_closed_start = None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    display_frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = display_frame.shape

    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark

            # EAR calculation for both eyes
            left_ear = calculate_ear(landmarks, LEFT_EYE, frame_w, frame_h)
            right_ear = calculate_ear(landmarks, RIGHT_EYE, frame_w, frame_h)
            avg_ear = (left_ear + right_ear) / 2.0

            # Drowsiness Check
            if avg_ear < EAR_THRESHOLD:
                if eyes_closed_start is None:
                    eyes_closed_start = time.time()
                
                elapsed_time = time.time() - eyes_closed_start

                # Show Warning Timer
                cv2.putText(display_frame, f'Eyes Closed: {elapsed_time:.1f}s', (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Trigger Alarm if time exceeds limit
                if elapsed_time >= CLOSED_TIME_LIMIT:
                    cv2.rectangle(display_frame, (0, 0), (frame_w, frame_h), (0, 0, 255), 10)
                    cv2.putText(display_frame, "DROWSINESS ALARM!", (100, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4)
                    
                    # Beep Sound (Frequency=2500Hz, Duration=100ms)
                    winsound.Beep(2500, 100)
            else:
                eyes_closed_start = None
                cv2.putText(display_frame, f'EAR: {avg_ear:.2f} (Awake)', (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Drowsiness Detection", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
