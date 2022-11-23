from turtle import st
from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
import ibm_db
import re

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ptc81939;PWD=F4Kdma3oL5ddCVAk",'','')
print(conn)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('homepage.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    print(session)
    print("Message - " + message)
    if session:
        if session["loggedin"]:
            return redirect(url_for('tracker'))
    else:
        login_page = True
        print(request.values.get('page'))
        if request.values.get('page') == "register":
            login_page = False
        return render_template('login.html', login=login_page, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        global message

        user = request.form
        print(user)
        email = user["email"]
        password = user["password"]

        print("Email - " + email + ", Password - " + password)

        sql = "SELECT * FROM users WHERE email = ? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ")
        print(account)

        if account:
            session['loggedin'] = True
            session['id'] = account['EMAIL']
            user_email = account['EMAIL']
            session['email'] = account['EMAIL']
            session['name'] = account['NAME']

            return redirect(url_for('tracker'))

        else:
            message = "Incorrect Email or Password"
            return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        global message

        user = request.form
        print(user)
        name = user["name"]
        email = user["email"]
        password = user["password"]

        sql = "SELECT * FROM USERS WHERE email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ", end="")
        print(account)

        if account:
            message = "Account already exists"
            return redirect(url_for('home', page="register"))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = "Invalid email address"
            return redirect(url_for('home', page="register"))
        elif not re.match(r'[A-Za-z0-9]+', name):
            message = "Name must contain only characters and numbers"
            return redirect(url_for('home', page="register"))
        else:
            insert_sql = "INSERT INTO users VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)

            session['loggedin'] = True
            session['id'] = email
            user_email = email
            session['email'] = email
            session['name'] = name

            message = ""

            return redirect(url_for('tracker'))


@app.route('/tracker')
def tracker():
    global message
    data = []
    expenses = {"Medical Expenses": 0, "House Expenses": 0, "Education": 0, "Savings": 0, "Others": 0}

    if session:
        if session["loggedin"]:
            sql = "SELECT date, title, category, amount FROM TRANSACTIONS WHERE email = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, session["email"])
            ibm_db.execute(stmt)

            row = ibm_db.fetch_assoc(stmt)
            while row:
                data.append(row)
                expenses[row["CATEGORY"]] += row["AMOUNT"]
                row = ibm_db.fetch_assoc(stmt)

            print(data)
            print(expenses)

            message = ""

            return render_template('home.html', name=session['name'], data=data[::-1], expenses=expenses)
    else:
        message = "Session Expired"
    return redirect(url_for("home"))


@app.route('/add-expenditure', methods=['GET', 'POST'])
def add_expenditure():
    if request.method == "POST":
        details = request.form
        print(details)

        date = details["date"][4:] + "-" + details["date"][5:7] + "-" + details["date"][:-2]
        title = details["title"]
        category = details["category"]
        amount = details["amount"]
        print(date, title, category, amount)

        sql = "INSERT INTO expenses VALUES (?, ?, ?, ?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, date)
        ibm_db.bind_param(stmt, 2, title)
        ibm_db.bind_param(stmt, 3, category)
        ibm_db.bind_param(stmt, 4, amount)
        ibm_db.bind_param(stmt, 5, session["email"])

        ibm_db.execute(stmt)

        return redirect(url_for('tracker'))


@app.route('/logout')
def logout():
    print("Logging Out")
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0")