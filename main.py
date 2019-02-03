from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ABA-Tracker:efficacy@localhost:8889/ABA-Tracker'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'supersecret'

class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    occurrences = db.Column(db.Integer)
    child_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    '''
    sessions = db.relationship('Session', backref='day')
'''
    def __init__(self, description, occurrences, child):
        self.description = description
        self.occurrences = occurrences
        self.child = child

'''
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    child_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    day_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))

    def __init__(self, number, owner, child, day):
        self.number = number
        self.owner = owner
        self.child = child
        self.day = day 
'''
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    behaviors = db.relationship('Behavior', backref='child')
    '''
    sessions = db.relationship('Session', backref='child')
'''
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    clients = db.relationship('Client', backref='owner')
    '''
    sessions = db.relationship('Session', backref='owner')
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    
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
    
    
@app.route('/signup', methods=['POST', 'GET']) 
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''

        # TODO = validate user's data
        
        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3:
            username_error = 'Need more characters'
            
        if username == '':
            username_error = 'Please enter username'
            username = ''

        if len(password) < 3:
            password_error = 'Need more characters'
            
        if len(password) == 0:
            password_error = 'Please enter password'
            password = ''
        
        if len(verify) < 3:
            verify_error = 'Need more characters'
           
        if len(verify) == 0:
            verify_error = 'Please enter password'
            verify = ''
        
        if password != verify:
            verify_error = 'Passwords do not match'
            verify = ''

        if existing_user != None and username == existing_user.username:
            username_error = 'Already exists'
            username = ''
        
        if username_error == '' and password_error == '' and verify_error == '':
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/home')
        else:
            return render_template('signup.html', title = 'ABA Data Tracker', username_error=username_error, password_error=password_error, verify_error=verify_error)
            
    return render_template('signup.html', title = 'ABA Data Tracker')

@app.route('/home')
def home():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('/index.html', title = 'ABA Data Tracker', user=user)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/home')

@app.route('/myclients')
def myclients():

    is_user = request.args.get('user')
    owner = User.query.filter_by(username=is_user).first()

    if is_user:
        user = Client.query.get(is_user)
        clients = Client.query.filter_by(owner=owner).all()
        return render_template('/myclients.html', title='My Clients', user=user, clients=clients)

    return render_template('/myclients.html', title= 'My Clients')

@app.route('/new-client', methods=['POST', 'GET'])
def new_client():

    client_error = ''

    if request.method == 'POST':
        client_name = request.form['client'] 
        
        if len(client_name) == 0 :
            client_error = 'Please enter name'  

        if not client_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_client = Client(client_name, owner)
            db.session.add(new_client)
            db.session.commit()
            '''
            /myclients?user={{user.username}}
            '''
            return redirect('/client?id=' + str(new_client.id))

        return render_template('/newclient.html',title="ABA Data Tracker", client_error=client_error)
    else:
        return render_template('/newclient.html')
    
    return render_template('/newclient.html')

@app.route('/new-behavior', methods=['POST', 'GET'])
def new_behavior():

    behavior_error = ''
    occurrences = 0
    is_id = request.args.get('id')
    child = Client.query.filter_by(id=is_id).first()
    behavior = Behavior.query.all()

    if request.method == 'POST':
        behavior_name = request.form['behavior']
        
        if len(behavior_name) == 0 :
            behavior_error = 'Please enter behavior'  

        if not behavior_error:   
            behavior = Behavior.query.all()
            new_behavior = Behavior(behavior_name, occurrences, child)
            db.session.add(new_behavior)
            db.session.commit()

            return redirect('/client?id=' + str(is_id))

        return render_template('/newbehavior.html',title="Add a New Behavior", behavior_error=behavior_error, behavior=behavior)
    else:
        return render_template('/newbehavior.html')

@app.route('/behavior', methods=['POST', 'GET'])
def behavior():
    
    is_id = request.args.get('id')

    if is_id:
        """
        def increment_behavior_occurrences():

        """
        behavior = Behavior.query.get(is_id)
        return render_template('/behavior.html', behavior=behavior)
    return render_template('/behavior.html')

@app.route('/client', methods=['POST', 'GET'])
def index():

    is_id = request.args.get('id')
    behaviors = Behavior.query.all()
    child = Client.query.filter_by(id=is_id).first()
    #child = Client.query.filter_by(id=is_id).first()
    
    if is_id:
        client = Client.query.get(is_id)
        behaviors = Behavior.query.filter_by(child=child).all()
        #behaviors = Behavior.query.all()
        return render_template('/clientpage.html', client=client, behaviors=behaviors)

    else:
        clients = Client.query.all()
        return render_template('/client.html',title="ABA Data Tracker", clients=clients)
        
if __name__ == '__main__':
    app.run(threaded = True)