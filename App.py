from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import face_recognition
import shutil

app = Flask(__name__)

# เส้นทางสำหรับแสดงรายการการเข้าร่วมทั้งหมด
@app.route('/')
def index():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    records = c.fetchall()
    conn.close()
    return render_template('index.html', records=records)

# เส้นทางสำหรับแสดงใบหน้าที่ไม่รู้จัก
@app.route('/unknown_faces')
def unknown_faces():
    unknown_images = []
    for filename in os.listdir('unknown_faces'):
        filepath = os.path.join('unknown_faces', filename)
        unknown_images.append(filepath)
    return render_template('unknown_faces.html', images=unknown_images)

# เส้นทางสำหรับระบุชื่อใบหน้าที่ไม่รู้จัก
@app.route('/add_known_face', methods=['POST'])
def add_known_face():
    name = request.form['name']
    image_path = request.form['image_path']

    # สร้างโฟลเดอร์สำหรับบุคคลถ้ายังไม่มี
    person_dir = os.path.join('known_faces', name)
    os.makedirs(person_dir, exist_ok=True)

    # ย้ายภาพจาก unknown_faces ไปยังโฟลเดอร์ของบุคคล
    new_image_path = os.path.join(person_dir, os.path.basename(image_path))
    shutil.move(image_path, new_image_path)

    # อัปเดตโมเดลการรู้จำใบหน้า
    image = face_recognition.load_image_file(new_image_path)
    encoding = face_recognition.face_encodings(image)
    if len(encoding) > 0:
        # บันทึกการเข้ารหัสและชื่อ
        # คุณอาจต้องจัดการการโหลดและบันทึกโมเดลใหม่หรือรีโหลดใน main.py
        pass  # สำหรับตัวอย่างนี้ เราจะข้ามขั้นตอนนี้ไปก่อน

    return redirect(url_for('unknown_faces'))

if __name__ == '__main__':
    app.run(debug=True)
import numpy as np
