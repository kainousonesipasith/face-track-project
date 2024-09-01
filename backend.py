from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/get_attendance_data')
def get_attendance_data():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT name, date, time, image_path FROM attendance")
    rows = c.fetchall()
    conn.close()

    attendance_data = []
    for row in rows:
        attendance_data.append({
            "name": row[0],
            "date": row[1],
            "time": row[2],
            "image_path": row[3]
        })

    return jsonify(attendance_data)

if __name__ == "__main__":
    app.run(debug=True)