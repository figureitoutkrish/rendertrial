from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Create table if not exists
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS students(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            sapid VARCHAR(50),
            age INTEGER,
            marks INTEGER,
            department VARCHAR(100)
        )
    """))
    conn.commit()

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":

        name = request.form["name"]
        sapid = request.form["sapid"]
        age = request.form["age"]
        marks = request.form["marks"]
        department = request.form["department"]

        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO students(name,sapid,age,marks,department)
                VALUES(:name,:sapid,:age,:marks,:department)
            """),{
                "name":name,
                "sapid":sapid,
                "age":age,
                "marks":marks,
                "department":department
            })
            conn.commit()

        return redirect("/")


    name = request.args.get("name")
    sapid = request.args.get("sapid")
    department = request.args.get("department")
    min_marks = request.args.get("min_marks")
    max_age = request.args.get("max_age")

    query = "SELECT * FROM students WHERE 1=1"
    params = {}

    if name:
        query += " AND LOWER(name) LIKE LOWER(:name)"
        params["name"] = f"%{name}%"

    if sapid:
        query += " AND sapid = :sapid"
        params["sapid"] = sapid

    if department:
        query += " AND LOWER(department) LIKE LOWER(:department)"
        params["department"] = f"%{department}%"

    if min_marks:
        query += " AND marks >= :min_marks"
        params["min_marks"] = int(min_marks)

    if max_age:
        query += " AND age <= :max_age"
        params["max_age"] = int(max_age)


    with engine.connect() as conn:
        students = conn.execute(text(query),params).fetchall()


    return render_template("index.html", students=students)