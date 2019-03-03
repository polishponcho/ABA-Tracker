from flask import Flask, Markup, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ABA-Tracker:efficacy@localhost:8889/ABA-Tracker'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'supersecret'

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    clients = db.relationship('Client', backref='owner')
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    behaviors = db.relationship('Behavior', backref='child')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    child_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    trackers = db.relationship('Tracker', backref='behavior')
    
    def __init__(self, description, child):
        self.description = description
        self.child = child

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(120))
    occurrences = db.Column(db.Integer)
    behavior_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))
    
    def __init__(self, datetime, occurrences, behavior):
        self.datetime = datetime
        self.occurrences = occurrences
        self.behavior = behavior

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/line')
def line():
 
    return render_template('line_chart.html', title='Bitcoin Monthly Price in USD')

# 0 (login, signup, and logout routes)

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

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/home')

# 1 home (Nav Bar, Title, App Description, and Link to "My Clients")

@app.route('/home')
def home():
    username = session['username']
    user = User.query.filter_by(username=username).first()
    return render_template('/index.html', title = 'Baseline', user=user)

# 2 myclients (List of users clients)

@app.route('/myclients')
def myclients():

    is_user = request.args.get('user')
    owner = User.query.filter_by(username=is_user).first()

    if is_user:
        user = Client.query.get(is_user)
        clients = Client.query.filter_by(owner=owner).all()
        return render_template('/myclients.html', title='My Clients', user=user, clients=clients)

    return render_template('/myclients.html', title= 'My Clients')

# 3 new-client (nav bar, title, <input submit, value='Add Client'/>)

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

# 4 

@app.route('/behavior', methods=['POST', 'GET'])
def behavior():
    
    is_id = request.args.get('id')
    behavior_id = Behavior.query.filter_by(id=is_id).first()
    trackers = Tracker.query.filter_by(behavior=behavior_id).all()
    behavior = Behavior.query.get(is_id)

    # graph visualization
    

    return render_template('/behavior.html', behavior=behavior, trackers=trackers)

@app.route('/increment-behavior', methods=['POST', 'GET'])
def increment_behavior():

    is_id = request.args.get('id')
    tracker = Tracker.query.get(is_id)

    if is_id:
        tracker = Tracker.query.get(is_id)
        db.session.query(Tracker).filter(Tracker.id==is_id).update({Tracker.occurrences: Tracker.occurrences + 1})
        db.session.commit()
        return render_template('/trackerpage.html', tracker=tracker, title='Track Behaviors Here!')

    else:
        return render_template('/trackerpage.html', tracker=tracker)

@app.route('/new-behavior', methods=['POST', 'GET'])
def new_behavior():

    behavior_error = ''
   
    is_id = request.args.get('id')
    child = Client.query.filter_by(id=is_id).first()
    behavior = Behavior.query.all()

    if request.method == 'POST':
        behavior_name = request.form['behavior']
        
        if len(behavior_name) == 0 :
            behavior_error = 'Please enter behavior'  

        if not behavior_error:   
            behavior = Behavior.query.all()
            new_behavior = Behavior(behavior_name, child)
            db.session.add(new_behavior)
            db.session.commit()

            return redirect('/client?id=' + str(is_id))

        return render_template('/newbehavior.html',title="Add a New Behavior", behavior_error=behavior_error, behavior=behavior)
    else:
        return render_template('/newbehavior.html')

@app.route('/client', methods=['POST', 'GET'])
def client():

    is_id = request.args.get('id')
    behaviors = Behavior.query.all()
    child = Client.query.filter_by(id=is_id).first()
    
    if is_id:
        client = Client.query.get(is_id)
        behaviors = Behavior.query.filter_by(child=child).all()
        return render_template('/clientpage.html', client=client, behaviors=behaviors)

    else:
        clients = Client.query.all()
        return render_template('/client.html', title="ABA Data Tracker", clients=clients)
        
@app.route('/tracker', methods=['POST', 'GET'])
def tracker():

    is_id = request.args.get('id')
    trackers = Tracker.query.all()
    
    behavior = Behavior.query.filter_by(id=is_id).first()
    
    if is_id:
        tracker = Tracker.query.get(is_id)
        trackerz = Tracker.query.filter_by(behavior=behavior).all()
        return render_template('/trackerpage.html', title='Track Behaviors Here!', tracker=tracker, behavior=behavior, trackerz=trackerz)

    return render_template('/tracker.html', title='Tracker Behaviors Here!', trackers=trackers, behavior=behavior)

@app.route('/new-aba-session', methods=['POST', 'GET'])
def new_aba_session():

    is_id = request.args.get('id')
    tracker_error = ''
    occurrences = 0
    behavior = Behavior.query.filter_by(id=is_id).first()
    behaviors = Behavior.query.all()

    if request.method == 'POST':
        tracker_datetime = request.form['date']

        if len(tracker_datetime) == 0 :
            tracker_error = 'Please enter date'

        if not tracker_error: 
            
            new_tracker = Tracker(tracker_datetime, occurrences, behavior)
            db.session.add(new_tracker)
            db.session.commit()

            return redirect('/tracker?id=' + str(new_tracker.id))
        return render_template('/newabasession.html', tracker_error=tracker_error, behaviors=behaviors)
    else:
        return render_template('/newabasession.html')

if __name__ == '__main__':
    app.run(threaded = True)