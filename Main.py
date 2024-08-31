import cv2
import sqlite3
import datetime
import os

# สร้างโฟลเดอร์ database และ face_images หากยังไม่มี
if not os.path.exists('database'):
    os.makedirs('database')
if not os.path.exists('face_images'):
    os.makedirs('face_images')

# เปิดใช้งานกล้อง
cap = cv2.VideoCapture(0)

# โหลดโมเดลตรวจจับใบหน้า
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# เชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect('database/attendance.db')
c = conn.cursor()

# สร้างตารางในฐานข้อมูลหากยังไม่มี
c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        name TEXT,
        date TEXT,
        time TEXT,
        image_path TEXT
    )
''')

conn.commit()

image_counter = 1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        scale_factor = 1.2  # ปรับขนาดสี่เหลี่ยมเป็น 120% ของขนาดเดิม
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)

        # คำนวณตำแหน่งใหม่ของสี่เหลี่ยม
        new_x = x - (new_w - w) // 2
        new_y = y - (new_h - h) // 2

        # วาดสี่เหลี่ยมใหม่
        cv2.rectangle(frame, (new_x, new_y), (new_x + new_w, new_y + new_h), (255, 0, 0), 2)

        # ตัดภาพใบหน้า
        face_image = frame[y:y+h, x:x+w]
        
        # บันทึกภาพใบหน้า
        face_image_path = f'face_images/face_{image_counter}.jpg'
        cv2.imwrite(face_image_path, face_image)
        
        # เพิ่มข้อมูลลงในฐานข้อมูล
        now = datetime.datetime.now()
        name = "Unknown"  # คุณสามารถปรับปรุงระบบการรู้จำใบหน้าเพื่อระบุชื่อได้
        c.execute("INSERT INTO attendance (name, date, time, image_path) VALUES (?, ?, ?, ?)", 
                  (name, now.date().isoformat(), now.time().isoformat(), face_image_path))
        conn.commit()

        image_counter += 1

    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()