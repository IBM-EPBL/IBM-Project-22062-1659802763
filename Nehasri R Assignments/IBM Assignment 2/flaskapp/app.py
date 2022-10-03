from flask import Flask,render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login.html')
def login():
    return render_template('login.html')  

@app.route('/signup.html')
def signup():
    return render_template('signup.html') 
