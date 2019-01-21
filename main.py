from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ABA-Tracker:efficacy@localhost:8889/ABA-Tracker'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

@app.route("/")
def index():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = ''
        password_error = ''
        user = User.query.filter_by(username=username).first()
        if user != None:
            if user.password != password:
                password_error = 'Invalid password'
        if user == None:
            username_error = 'Username does not exist'
                
        if user and user.password == password:
            session['username'] = username
            return redirect('/home')
        else:
            return render_template('login.html', username_error=username_error, password_error=password_error)

    return render_template('login.html')


@app.route('/signup') 
def signup():

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(threaded = True)