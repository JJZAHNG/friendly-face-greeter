import os
import sys
import time
import random
import threading
import queue
import subprocess

import cv2
import numpy as np
import face_recognition

# ———— 1. 异步 TTS 线程与队列 ————
tts_queue = queue.Queue()

def tts_worker():
    """
    后台线程不断从队列中取出消息，用系统 say 命令播放（阻塞在此线程，不影响主线程）。
    """
    while True:
        msg = tts_queue.get()
        if msg is None:  # 结束信号
            break
        # 调用 macOS say，-v Kathy 指定 Kathy 女声
        subprocess.run(["say", "-v", "Kathy", msg])
        tts_queue.task_done()

# 启动后台 TTS 线程
threading.Thread(target=tts_worker, daemon=True).start()


# ———— 2. 英文寒暄短句列表 ————
small_talk_phrases = [
    "How are you today?",
    "Nice to see you!",
    "Hope you're having a great day!",
    "What’s new with you?",
    "Good to see you again!"
]


# ———— 3. 加载已知人脸库 ————
known_face_encodings = []
known_face_names = []
known_faces_dir = 'known_faces'

for filename in os.listdir(known_faces_dir):
    if not filename.lower().endswith(('.jpg', '.png')):
        continue
    name = os.path.splitext(filename)[0]
    path = os.path.join(known_faces_dir, filename)

    img_bgr = cv2.imread(path)
    if img_bgr is None:
        print(f"❌ Cannot open file: {filename}")
        continue

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    # 尝试 HOG + CNN 两种模型检测
    for model in ('hog', 'cnn'):
        locs = face_recognition.face_locations(img_rgb, model=model)
        if locs:
            encs = face_recognition.face_encodings(img_rgb, known_face_locations=locs)
            if encs:
                known_face_encodings.append(encs[0])
                known_face_names.append(name)
                print(f"✅ Loaded: {name} (model={model}, faces_detected={len(locs)})")
                break
    else:
        print(f"⚠️ Warning: no faces found in {filename}")

if not known_face_encodings:
    print("❌ No known faces loaded. Exiting.")
    sys.exit(1)


# ———— 4. 打开摄像头 ————
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    sys.exit(1)


# ———— 5. 问候记录 & 设置 ————
greeted_times = {}         # { name: last_greet_timestamp }
GREET_INTERVAL = 60        # 同一人至少隔 60 秒再问候


# ———— 6. 主循环：检测、识别、异步问候 ————
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 缩小帧，加速人脸检测
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 检测人脸位置与编码
        face_locs = face_recognition.face_locations(rgb_small)
        face_encs = face_recognition.face_encodings(rgb_small, face_locs)

        # 准备找第一位符合问候条件的人
        now = time.time()
        to_greet = None
        greet_name = None

        # 遍历检测到的所有人脸
        for (top, right, bottom, left), enc in zip(face_locs, face_encs):
            matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=0.5)
            if True in matches:
                idx = np.argmin(face_recognition.face_distance(known_face_encodings, enc))
                if matches[idx]:
                    name = known_face_names[idx]
                    last = greeted_times.get(name, 0)
                    if now - last > GREET_INTERVAL:
                        # 只选第一位满足条件的人来问候
                        phrase = random.choice(small_talk_phrases)
                        to_greet = f"Hello, {name}! {phrase}"
                        greet_name = name
                        break  # 不再考虑其他人

        # 如果有要问候的，放到 TTS 队列
        if to_greet:
            tts_queue.put(to_greet)
            greeted_times[greet_name] = now

        # 绘制所有检测到的人脸框和姓名
        for (top, right, bottom, left), enc in zip(face_locs, face_encs):
            # 再次匹配以获得姓名
            matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=0.5)
            name = "Stranger"
            if True in matches:
                idx = np.argmin(face_recognition.face_distance(known_face_encodings, enc))
                if matches[idx]:
                    name = known_face_names[idx]
            # 恢复到原始大图坐标
            t, r, b, l = top*4, right*4, bottom*4, left*4
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
            cv2.putText(frame, name, (l, t-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 显示视频
        cv2.imshow('Face Greeting', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 关闭摄像头窗口
    cap.release()
    cv2.destroyAllWindows()
    # 停止 TTS 线程
    tts_queue.put(None)
    tts_queue.join()
