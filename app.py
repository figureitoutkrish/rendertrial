from flask import Flask, request, jsonify, send_file
import psycopg
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        sap TEXT PRIMARY KEY,
        name TEXT,
        age INT,
        marks INT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()


@app.route("/")
def home():
    return send_file("app.html")


@app.route("/add_student", methods=["POST"])
def add_student():

    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students VALUES (%s,%s,%s,%s) ON CONFLICT (sap) DO UPDATE SET name=%s, age=%s, marks=%s",
        (data["sap"], data["name"], data["age"], data["marks"],
         data["name"], data["age"], data["marks"])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message":"Student added"})


@app.route("/get_student/<sap>")
def get_student(sap):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE sap=%s",(sap,))
    student = cur.fetchone()

    cur.close()
    conn.close()

    if student:
        return jsonify({
            "sap":student[0],
            "name":student[1],
            "age":student[2],
            "marks":student[3]
        })

    return jsonify({"message":"Student not found"})

@app.route("/get_all_students")
def get_all_students():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    students = []

    for row in rows:
        students.append({
            "sap": row[0],
            "name": row[1],
            "age": row[2],
            "marks": row[3]
        })

    return jsonify(students)