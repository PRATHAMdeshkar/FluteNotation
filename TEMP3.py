# this code will work on down action of fingers
import cv2
import mediapipe as mp

# Initialize Mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# =========================================
# Utility: Check if finger is UP
# =========================================
def is_finger_up(hand_landmarks, tip_idx, pip_idx):
    # y is inverted (top=0, bottom=1), so smaller y = higher (up)
    return hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[pip_idx].y

# Get pattern of 6 fingers (ignoring thumb + pinky)
def get_finger_pattern(results):
    # Pattern = [L_index, L_middle, L_ring, R_index, R_middle, R_ring]
    pattern = [0, 0, 0, 0, 0, 0]

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        left_hand = results.multi_hand_landmarks[0]
        right_hand = results.multi_hand_landmarks[1]

        # Left hand
        pattern[0] = 1 if is_finger_up(left_hand, 8, 6) else 0   # Index
        pattern[1] = 1 if is_finger_up(left_hand, 12, 10) else 0 # Middle
        pattern[2] = 1 if is_finger_up(left_hand, 16, 14) else 0 # Ring

        # Right hand
        pattern[3] = 1 if is_finger_up(right_hand, 8, 6) else 0
        pattern[4] = 1 if is_finger_up(right_hand, 12, 10) else 0
        pattern[5] = 1 if is_finger_up(right_hand, 16, 14) else 0

    return pattern

# Map finger pattern → Note
def detect_note(pattern):
    # 1 = finger UP, 0 = finger DOWN
    if pattern == [1,1,1,0,0,0]: return "Sa"
    elif pattern == [1,0,0,0,0,0]: return "Re"
    elif pattern == [1,1,0,0,0,0]: return "Ga"
    elif pattern == [0,0,0,0,0,0]: return "Pa"
    elif pattern == [1,1,1,1,1,0]: return "Dha"
    elif pattern == [1,1,1,1,1,1]: return "Ni"
    else: return "Unknown"

# =========================================
# Main Loop
# =========================================
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    note = "No hands"
    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        # Draw both hands
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

        # Detect pattern & map to note
        pattern = get_finger_pattern(result)
        note = detect_note(pattern)

        # Show finger pattern for debugging
        cv2.putText(frame, f"Pattern: {pattern}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # Show detected note
    cv2.putText(frame, f"Note: {note}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Flute Notation Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
