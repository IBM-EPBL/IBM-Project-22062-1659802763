from flask import Flask, render_template, request, redirect, session 

import ibm_db
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


app = Flask(__name__)


app.secret_key = 'team23362'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ptc81939;PWD=F4Kdma3oL5ddCVAk",'','')

#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")



#SIGN--UP--OR--REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        

        sql = "SELECT * FROM REGISTERUSER WHERE USERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            sql1="INSERT INTO REGISTERUSER(USERNAME,PASSWORD,EMAIL) VALUES(?,?,?)"
            stmt1 = ibm_db.prepare(conn, sql1)
            
            ibm_db.bind_param(stmt1,1,username)
            ibm_db.bind_param(stmt1,2,password)
            ibm_db.bind_param(stmt1,3,email)
            ibm_db.execute(stmt1)
            msg = 'You have successfully registered !'
            return render_template('signup.html', msg = msg)

           
        
 #LOGIN--PAGE    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    msg = ''
  
    if request.method == 'POST' :
        
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM REGISTERUSER WHERE USERNAME =? AND PASSWORD =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        
        if account:
            session['loggedin'] = True
            session['username'] = account["USERNAME"]
            session['email']=account["EMAIL"]
           
            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

#ADDING----DATA
@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    id=request.form['id']
    date = request.form['date']
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']

    sql = "INSERT INTO EXPENSES1(USERID,DATE,TITLE,AMOUNT,CATEGORY) VALUES(?,?,?,?,?)"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,id)
    ibm_db.bind_param(stmt,2,date)
    ibm_db.bind_param(stmt,3,title)
    ibm_db.bind_param(stmt,4,amount)
    ibm_db.bind_param(stmt,5,category)
    ibm_db.execute(stmt)
    
  
    print(date + " " + title + " " + amount + " " + category)

    sql1 = "SELECT * FROM EXPENSES1 WHERE MONTH(date)=MONTH(DATE(NOW()))"
    stmt1 = ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    list2=[]
    expense1 = ibm_db.fetch_tuple(stmt1)
    while(expense1):
        list2.append(expense1)
        expense1 = ibm_db.fetch_tuple(stmt1)
    total = 0
    for x in list2:
        total+= x[3]

    sql2 = "SELECT explimit FROM LIMITS  DESC LIMIT 1"
    stmt2 = ibm_db.prepare(conn, sql2)
    ibm_db.execute(stmt2)
    limit=ibm_db.fetch_tuple(stmt2)

    if(total>limit[0]):
        
        
        mail_from = '19i304@psgtech.ac.in'
        mail_to = session['email']

        msg = MIMEMultipart()
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Subject'] = 'Expense Alert Limit'
        mail_body = """
        Dear User, You have exceeded the specified monthly expense Limit!!!!

        """
        msg.attach(MIMEText(mail_body))

        try:
            server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
            server.ehlo()
            server.login('apikey', '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')
            server.sendmail(mail_from, mail_to, msg.as_string())
            server.close()
            print("mail sent")
        except:
            print("issue")

    
    return redirect("/display")



#DISPLAY---graph 

@app.route("/display")
def display():
    print(session["username"])
    
    sql = "SELECT * FROM EXPENSES1 "
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    list1=[]
    row = ibm_db.fetch_tuple(stmt)
    while(row):
        list1.append(row)
        row = ibm_db.fetch_tuple(stmt)
    print(list1)

    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in list1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]    
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
        elif x[6] == "EMI":
            t_EMI  += x[4]
        elif x[6] == "other":
            t_other  += x[4]
    

    

    
    return render_template('display.html' ,expense = list1,total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other)
                          


@app.route('/update', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      title = request.form['title']
      amount = request.form['amount']
      category = request.form['category']
      userid= request.form['userid']
    
      

      sql = "UPDATE expenses SET date =? , title =? , amount =?, category =? WHERE expenses.userid =? "
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,date)
      ibm_db.bind_param(stmt,2,title)
      ibm_db.bind_param(stmt,3,amount)
      ibm_db.bind_param(stmt,4,category)
      ibm_db.bind_param(stmt,5,userid)
      ibm_db.execute(stmt)

      print('successfully updated')
      return redirect("/display")
     
 #limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
         userid=request.form['id']
         number= request.form['number']
         

         sql = "INSERT INTO LIMITS(USERID,EXPLIMIT) VALUES(?,?)"
         stmt = ibm_db.prepare(conn, sql)
         ibm_db.bind_param(stmt,1,userid)
         ibm_db.bind_param(stmt,2,number)
         ibm_db.execute(stmt)
         return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    

    sql = "SELECT EXPLIMIT FROM LIMITS DESC LIMIT 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row=ibm_db.fetch_tuple(stmt)
    
    
    return render_template("limit.html" , y= row)

#REPORT

@app.route("/today")
def today():
      
      sql = "SELECT * FROM expenses1  WHERE date = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list2=[]
      texpense=ibm_db.fetch_tuple(stmt)
      print(texpense)
      
      

      sql = "SELECT * FROM EXPENSES1 WHERE DATE(date) = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)  
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      


     
      return render_template("today.html", texpense = list1, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
      

      sql = "SELECT MONTHNAME(DATE),SUM(AMOUNT) FROM EXPENSES1 GROUP BY MONTHNAME(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)
      
      

      sql = "SELECT * FROM EXPENSES1 WHERE MONTH(date)=MONTH(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("month.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
      
      
      sql = "SELECT YEAR(DATE),SUM(AMOUNT) FROM EXPENSES1 GROUP BY YEAR(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)


      

      sql = "SELECT * FROM EXPENSES1 WHERE YEAR(date)=YEAR(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("year.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('username', None)
   session.pop('email',None)
   return render_template('home.html')

             

if __name__ == "__main__":
    app.run(debug=True)