import cv2
import mediapipe as mp
import socket

ESP32_IP = "10.91.247.124"
ESP32_PORT = 4210

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8, max_num_hands=1)
cap = cv2.VideoCapture(0)

FINGER_TIPS = [8, 12, 16, 20]
THUMB_TIP = 4
THUMB_IP = 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark
        hand_label = results.multi_handedness[0].classification[0].label

        fingers_extended = 0

        for tip in FINGER_TIPS:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers_extended += 1

        if hand_label == "Right":
            if landmarks[THUMB_TIP].x < landmarks[THUMB_IP].x:
                fingers_extended += 1
        else:
            if landmarks[THUMB_TIP].x > landmarks[THUMB_IP].x:
                fingers_extended += 1

        try:
            sock.sendto(str(fingers_extended).encode(), (ESP32_IP, ESP32_PORT))
            print(f"Sent data: {fingers_extended}")
        except Exception as e:
            print(f"Error sending data: {e}")

        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.putText(frame, f'Fingers: {fingers_extended}', (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Finger Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
