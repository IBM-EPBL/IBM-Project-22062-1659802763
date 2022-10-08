from flask import Flask,render_template, request, redirect, session 
from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
app.debug = True
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
 
db = SQLAlchemy(app)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
 
    def __repr__(self):
        return f"Name : {self.name}, Email: {self.email}"
 

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/index.html')
def index():
    profiles = Profile.query.all()
    return render_template('index.html', profiles=profiles)
 
@app.route('/login.html')
def login():
    return render_template('login.html')  

@app.route('/signup.html')
def signup():
    return render_template('signup.html') 

@app.route('/add', methods=["POST"])
def profile():

    name = request.form.get("name")
    email = request.form.get("email")
 
    if name != '' and email != '' :
        p = Profile(name=name, email=email)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')
 
@app.route('/delete/<int:id>')
def erase(id):
     
    data = Profile.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/homepage.html')

if __name__ == '__main__':
    app.run()
