from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "Nandu25"


# ----------- DATABASE CREATION -----------
def create_db():
    if not os.path.exists("database.db"):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE admin (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regno TEXT,
                name TEXT,
                branch TEXT,
                year TEXT,
                cgpa REAL
            )
        """)

        cur.execute("INSERT INTO admin(username, password) VALUES('Bala Nandu','Nandu25')")
        con.commit()
        con.close()

create_db()


# ----------- LOGIN -----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (u, p))
        data = cur.fetchone()
        con.close()

        if data:
            session["admin"] = u
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")



# ----------- STUDENT LIST -----------
@app.route("/students")
def students():
    if "admin" not in session:
        return redirect("/")

    search = request.args.get("search", "")

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
    SELECT * FROM students 
    WHERE name LIKE ? 
       OR regno LIKE ?
       OR cgpa LIKE ?
       OR year LIKE ?
       OR branch LIKE ?         
""", ("%" + search + "%", "%" + search + "%", "%" + search + "%","%" + search + "%","%" + search + "%"))
    data = cur.fetchall()
    con.close()

    return render_template("students.html", students=data, search=search)


# ----------- ADD STUDENT -----------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        regno = request.form["regno"]
        name = request.form["name"]
        branch = request.form["branch"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]

        con = sqlite3.connect("database.db")
        con.execute("INSERT INTO students(regno,name,branch,year,cgpa) VALUES(?,?,?,?,?)",
                    (regno, name, branch, year, cgpa))
        con.commit()
        con.close()

        return redirect("/students")

    return render_template("add.html")


# ----------- EDIT STUDENT -----------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "admin" not in session:
        return redirect("/")

    con = sqlite3.connect("database.db")
    cur = con.cursor()

    if request.method == "POST":
        regno = request.form["regno"]
        name = request.form["name"]
        branch = request.form["branch"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]

        cur.execute("""
            UPDATE students SET regno=?, name=?, branch=?, year=?, cgpa=? WHERE id=?
        """, (regno, name, branch, year, cgpa, id))

        con.commit()
        con.close()

        return redirect("/students")

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    data = cur.fetchone()
    con.close()

    return render_template("edit.html", student=data)


# ----------- DELETE STUDENT -----------
@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect("/")

    con = sqlite3.connect("database.db")
    con.execute("DELETE FROM students WHERE id=?", (id,))
    con.commit()
    con.close()

    return redirect("/students")


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")

    con = sqlite3.connect("database.db")
    cur = con.cursor()

    # Fetch Names + CGPA for chart
    cur.execute("SELECT name, cgpa FROM students")
    data = cur.fetchall()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    students_count = cur.fetchone()[0]

    # Average CGPA
    cur.execute("SELECT AVG(cgpa) FROM students")
    avg_cgpa = cur.fetchone()[0]
    avg_cgpa = round(avg_cgpa, 2) if avg_cgpa else 0

    # Highest CGPA
    cur.execute("SELECT MAX(cgpa) FROM students")
    max_cgpa = cur.fetchone()[0] or 0

    # Lowest CGPA
    cur.execute("SELECT MIN(cgpa) FROM students")
    min_cgpa = cur.fetchone()[0] or 0

    con.close()

    # Prepare chart data
    names = [x[0] for x in data]
    cgpa = [x[1] for x in data]

    return render_template(
        "dashboard.html",
        names=names,
        cgpa=cgpa,
        students_count=students_count,
        avg_cgpa=avg_cgpa,
        max_cgpa=max_cgpa,
        min_cgpa=min_cgpa
    )



# ----------- RUN SERVER -----------
if __name__ == "__main__":
    app.run(debug=True)
