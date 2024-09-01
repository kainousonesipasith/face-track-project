import cv2
import face_recognition
import os
import numpy as np
import sqlite3
import datetime

# สร้างโฟลเดอร์หากยังไม่มี
os.makedirs('known_faces', exist_ok=True)
os.makedirs('unknown_faces', exist_ok=True)

# โหลดข้อมูลใบหน้าที่รู้จัก
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for name in os.listdir('known_faces'):
        person_dir = os.path.join('known_faces', name)
        if not os.path.isdir(person_dir):
            continue
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)
    return known_face_encodings, known_face_names

known_face_encodings, known_face_names = load_known_faces()

# เชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# สร้างตารางหากยังไม่มี
c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT,
        image_path TEXT
    )
''')
conn.commit()

# เริ่มต้นการจับภาพจากกล้อง
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # ย่อขนาดเฟรมเพื่อเพิ่มความเร็วในการประมวลผล
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # ค้นหาใบหน้าและการเข้ารหัสในเฟรมปัจจุบัน
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

        top, right, bottom, left = face_location
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # บันทึกภาพใบหน้า
        face_image = frame[top:bottom, left:right]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if name == "Unknown":
            os.makedirs('unknown_faces', exist_ok=True)
            image_path = f'unknown_faces/unknown_{timestamp}.jpg'
        else:
            person_dir = os.path.join('known_faces', name)
            os.makedirs(person_dir, exist_ok=True)
            image_path = os.path.join(person_dir, f'{timestamp}.jpg')
        cv2.imwrite(image_path, face_image)

        # บันทึกข้อมูลลงฐานข้อมูล
        now = datetime.datetime.now()
        c.execute('''
            INSERT INTO attendance (name, date, time, image_path)
            VALUES (?, ?, ?, ?)
        ''', (name, now.date().isoformat(), now.time().strftime("%H:%M:%S"), image_path))
        conn.commit()

        # วาดกรอบและชื่อบนเฟรม
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # แสดงผลเฟรม
    cv2.imshow('Video', frame)

    # กด 'q' เพื่อออก
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดการเชื่อมต่อ
video_capture.release()
cv2.destroyAllWindows()
conn.close()
