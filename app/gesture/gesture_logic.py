import cv2
import mediapipe as mp
import pyautogui
import math
import time

# =========================
# CORE PARAMETERS
# =========================
FRAME_MARGIN = 0.15
EDGE_MARGIN = 6
HAND_LOST_TIMEOUT = 0.4

MIN_GAIN = 0.8
MAX_GAIN = 2.4
MIN_SMOOTH = 0.08
MAX_SMOOTH = 0.30
VELOCITY_DEADZONE = 2.5

CLICK_DISTANCE = 0.06
DOUBLE_CLICK_DISTANCE = 0.025

SCROLL_SPEED = 120
SCROLL_COOLDOWN = 0.12

# =========================
# UTILS
# =========================
def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def clamp(v, mn, mx):
    return max(mn, min(mx, v))

def finger_up(tip, pip):
    return tip.y < pip.y

# =========================
# MAIN
# =========================
def run_gesture_mouse(controller):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    screen_w, screen_h = pyautogui.size()
    prev_x, prev_y = pyautogui.position()

    last_hand_time = time.time()
    last_scroll_time = 0
    last_click_time = 0

    dragging = False

    window = "Gesture Mouse"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    while controller.active:
        ok, frame = cap.read()
        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if res.multi_hand_landmarks:
            last_hand_time = time.time()
            hand = res.multi_hand_landmarks[0]
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand, mp_hands.HAND_CONNECTIONS
            )

            thumb = hand.landmark[4]
            index = hand.landmark[8]
            middle = hand.landmark[12]
            ring = hand.landmark[16]
            pinky = hand.landmark[20]

            index_pip = hand.landmark[6]
            middle_pip = hand.landmark[10]
            ring_pip = hand.landmark[14]
            pinky_pip = hand.landmark[18]

            index_up = finger_up(index, index_pip)
            middle_up = finger_up(middle, middle_pip)
            ring_up = finger_up(ring, ring_pip)
            pinky_up = finger_up(pinky, pinky_pip)

            now = time.time()

            # =========================
            # DRAG MODE (FIST)
            # =========================
            if not index_up and not middle_up and not ring_up and not pinky_up:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
                cv2.putText(frame, "DRAG", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)

            # =========================
            # RELEASE DRAG (OPEN HAND)
            # =========================
            elif index_up and middle_up and ring_up and pinky_up:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            # =========================
            # CURSOR MOVE (INDEX + MIDDLE ONLY)
            # =========================
            if index_up and middle_up and not ring_up and not pinky_up:
                raw_x = (1 - index.x - FRAME_MARGIN) / (1 - 2 * FRAME_MARGIN) * screen_w
                raw_y = (index.y - FRAME_MARGIN) / (1 - 2 * FRAME_MARGIN) * screen_h

                raw_x = clamp(raw_x, EDGE_MARGIN, screen_w - EDGE_MARGIN)
                raw_y = clamp(raw_y, EDGE_MARGIN, screen_h - EDGE_MARGIN)

                dx = raw_x - prev_x
                dy = raw_y - prev_y
                speed = math.hypot(dx, dy)

                if speed < VELOCITY_DEADZONE:
                    raw_x, raw_y = prev_x, prev_y

                gain = clamp(MIN_GAIN + speed / 30, MIN_GAIN, MAX_GAIN)
                smooth = clamp(MAX_SMOOTH - speed / 50, MIN_SMOOTH, MAX_SMOOTH)

                prev_x += (raw_x - prev_x) * smooth * gain
                prev_y += (raw_y - prev_y) * smooth * gain

                pyautogui.moveTo(int(prev_x), int(prev_y))

                # -------- DOUBLE CLICK --------
                if abs(index.x - middle.x) < DOUBLE_CLICK_DISTANCE:
                    pyautogui.doubleClick()
                    time.sleep(0.4)

            # =========================
            # LEFT CLICK (UNCHANGED)
            # =========================
            if (
                distance(index, thumb) < CLICK_DISTANCE and
                now - last_click_time > 0.5
            ):
                pyautogui.click()
                last_click_time = now

            # =========================
            # RIGHT CLICK (UNCHANGED)
            # =========================
            if (
                distance(pinky, thumb) < CLICK_DISTANCE and
                now - last_click_time > 0.5
            ):
                pyautogui.rightClick()
                last_click_time = now

            # =========================
            # SCROLL / VOLUME / BRIGHTNESS
            # =========================
            if (
                distance(index, thumb) < CLICK_DISTANCE and
                not middle_up and not ring_up and not pinky_up and
                now - last_scroll_time > SCROLL_COOLDOWN
            ):
                dx = index.x - thumb.x
                dy = index.y - thumb.y

                if abs(dy) > abs(dx):
                    pyautogui.scroll(int(-dy * SCROLL_SPEED))
                else:
                    pyautogui.hscroll(int(dx * SCROLL_SPEED))

                last_scroll_time = now

        # =========================
        # HAND LOST SAFETY
        # =========================
        if time.time() - last_hand_time > HAND_LOST_TIMEOUT:
            if dragging:
                pyautogui.mouseUp()
                dragging = False

        cv2.imshow(window, frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
