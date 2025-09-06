import cv2
import mediapipe as mp
from kafka import KafkaProducer
import json, time

# ==============================
# Kafka Producer Setup
# ==============================
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ==============================
# MediaPipe Setup
# ==============================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# ==============================
# Utility: Check if finger is up
# ==============================
def is_finger_up(hand_landmarks, tip_id, pip_id):
    return hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y

# ==============================
# Get finger status (index, middle, ring)
# ==============================
def get_finger_status(hand_landmarks, handedness):
    finger_map = {
        "index": (8, 6),
        "middle": (12, 10),
        "ring": (16, 14),
    }

    status = {}
    for finger, (tip, pip) in finger_map.items():
        is_up = is_finger_up(hand_landmarks, tip, pip)
        hole_closed = not is_up   # closed if finger is down
        key = f"{handedness}_{finger}"
        status[key] = hole_closed
    return status

# ==============================
# Map holes → Note
# ==============================
def get_flute_note(hole_status):
    holes = [
        hole_status.get("left_index", False),   # Hole 1
        hole_status.get("left_middle", False),  # Hole 2
        hole_status.get("left_ring", False),    # Hole 3
        hole_status.get("right_index", False),  # Hole 4
        hole_status.get("right_middle", False), # Hole 5
        hole_status.get("right_ring", False),   # Hole 6
    ]

    # Convert to pattern
    pattern = ''.join(['1' if h else '0' for h in holes])

    note_map = {
        "111000": "Sa",
        "110000": "Re",
        "100000": "Ga",
        "000000": "Ma",
        "111111": "Pa",
        "111110": "Dha",
        "111100": "Ni",
    }

    return note_map.get(pattern, "Unknown"), pattern

# ==============================
# Webcam Loop
# ==============================
cap = cv2.VideoCapture(0)

print("🎵 Hand gesture detection started... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    h, w, _ = frame.shape
    all_finger_status = {}

    if result.multi_hand_landmarks and result.multi_handedness:
        for handLms, handLabel in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            handedness = handLabel.classification[0].label.lower()  # "left" or "right"
            finger_status = get_finger_status(handLms, handedness)
            all_finger_status.update(finger_status)

    # Detect note + pattern
    note, pattern = get_flute_note(all_finger_status)

    # Show on screen
    cv2.putText(frame, f"Note: {note}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Pattern: {pattern}", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Send to Kafka
    if note != "Unknown":
        event = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "pattern": pattern,
            "note": note
        }
        producer.send("flute_notes", event)
        print("Produced:", event)

    cv2.imshow("Flute Note Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
