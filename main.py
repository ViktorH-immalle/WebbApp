from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user
from sqlite3 import connect, Cursor
import logging

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.logger.disabled = True
mylog  = logging.getLogger('werkzeug')
mylog.disabled = True



class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.environ['REMOTE_ADDR']
    if request.method == 'POST':
        db = connect('database')
        cur = db.cursor()
        formUsername = request.form['username']
        formPassword = request.form['password']
        cur.execute('SELECT * FROM user WHERE username ="' + str(formUsername) + '" AND password ="' + str(formPassword) + '";')
        data = cur.fetchall()
        if len(data) == 0:
            print('# ' + ip + ' Just tried to login with a not existing account.' )
            return 'This account does not exist!'
        else:
            print('# ' + ip + ' Logged on with username: ' + formUsername )
            cur.execute('SELECT userid FROM user WHERE username="' + formUsername + '" AND password ="' + formPassword + '";')
            userid = cur.fetchone()[0]
            login_user(User(userid))
            return render_template('dashboard.html')
    return render_template('auth.html')

@app.route('/agenda', methods=['GET', 'POST'])
@login_required
def agenda():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    ip = request.environ['REMOTE_ADDR']
    print('# ' + ip + ' Logged out.')
    logout_user()
    return redirect(url_for('login'))

@app.route('/createuser', methods=['GET','POST'])
def createuser():
    ip = request.environ['REMOTE_ADDR']
    if request.method == 'POST':
        database = connect('database')
        cur = database.cursor()
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        cur.execute('INSERT OR IGNORE INTO user (email, username, password) VALUES("' + email + '","' + username + '","' + password + '");')
        database.commit()

        if cur.lastrowid == 0:
            print('# ' + ip + ' Tried to create a user that already exists:' + username)
            return redirect(url_for('createuser'))
        else:
            print('# ' + ip + ' Created new user, username: ' + username + ' email: ' + email)  
            return redirect(url_for('login'))
    return render_template('CreateUser.html')

@app.route('/creategroup', methods=['GET', 'POST'])
@login_required
def creategroup():
    ip = request.environ['REMOTE_ADDR']
    if request.method == 'POST':
        database = connect('database')
        cur = database.cursor()
        groupname = request.form['groupname']

        cur.execute('INSERT OR IGNORE INTO groep (groupname) VALUES("' + groupname +'");')
        database.commit()
        if cur.lastrowid == 0:
            print('# ' + ip + ' Tried to create a group that already exists: ' + groupname)
            return render_template('CreateGroup.html', message = 'Groep already exists!')   
        else:
            print('# ' + ip + ' Created a new group named: ' + groupname)    
            return redirect(url_for('agenda'))
        return render_template('dashboard.html')
    return render_template('CreateGroup.html')

@app.route('/agenda/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
    if request.method == 'POST':
        database = connect('database')
        cur = database.cursor()
        post = request.form['post']
        date = request.form['date']
    return render_template('newpost.html')

if __name__ == "__main__":
    app.secret_key = "123"
    app.run(debug=1, host='0.0.0.0')