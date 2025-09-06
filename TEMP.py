# this code works on fingers down
import cv2
import mediapipe as mp

# Initialize Mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# =========================================
# Utility: Check if finger is "down" (hole closed)
# =========================================
def is_finger_down(hand_landmarks, tip_idx, pip_idx):
    return hand_landmarks.landmark[tip_idx].y > hand_landmarks.landmark[pip_idx].y

# Map holes 1–6 from two hands
def get_hole_pattern(results):
    # Default: all open
    holes = [0, 0, 0, 0, 0, 0]

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        # Assume first hand is left, second is right
        left_hand = results.multi_hand_landmarks[0]
        right_hand = results.multi_hand_landmarks[1]

        # Left hand → Holes 1–3
        holes[0] = 1 if is_finger_down(left_hand, 8, 6) else 0  # Index
        holes[1] = 1 if is_finger_down(left_hand, 12, 10) else 0  # Middle
        holes[2] = 1 if is_finger_down(left_hand, 16, 14) else 0  # Ring

        # Right hand → Holes 4–6
        holes[3] = 1 if is_finger_down(right_hand, 8, 6) else 0  # Index
        holes[4] = 1 if is_finger_down(right_hand, 12, 10) else 0  # Middle
        holes[5] = 1 if is_finger_down(right_hand, 16, 14) else 0  # Ring

    return holes

# Map hole pattern → Note
def detect_note(holes):
    # holes = [H1, H2, H3, H4, H5, H6] where 1=closed, 0=open
    if holes == [1,1,1,0,0,0]: return "Sa"
    elif holes == [1,1,0,0,0,0]: return "Re"
    elif holes == [1,0,0,0,0,0]: return "Ga"
    elif holes == [0,0,0,0,0,0]: return "Ma"
    elif holes == [1,1,1,1,1,1]: return "Pa"
    elif holes == [1,1,1,1,1,0]: return "Dha"
    elif holes == [1,1,1,1,0,0]: return "Ni"
    else: return "Unknown"

# =========================================
# Main loop
# =========================================
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    note = "No hands"
    pattern = [0,0,0,0,0,0]

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        # Draw both hands
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

        # Get pattern and detect note
        pattern = get_hole_pattern(result)
        note = detect_note(pattern)

    # Show note on screen
    cv2.putText(frame, f"Note: {note}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # Show pattern on screen
    cv2.putText(frame, f"Pattern: {pattern}", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    # Display video
    cv2.imshow("Flute Notation Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
