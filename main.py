from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user
from sqlite3 import connect, Cursor

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = connect('database')
        cur = db.cursor()
        formUsername = request.form['username']
        formPassword = request.form['password']
        cur.execute('SELECT * FROM user WHERE username ="' + formUsername + '" AND Password ="' + formPassword + '";')
        data = cur.fetchall()
        if len(data) == 0:
            return 'False'
        else:
            cur.execute('SELECT userid FROM user WHERE username ="' + formUsername + '" AND Password ="' + formPassword + '";')
            userid = cur.fetchone()[0]
            login_user(User(userid))
            return render_template('Agenda.html')

    return render_template('Login.html')

@app.route('/agenda')
@login_required
def agenda():
    return render_template('Agenda.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/createuser', methods=['GET','POST'])
def createuser():
    if request.method == 'POST':
        database = connect('database')
        cur = database.cursor()
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        cur.execute('INSERT OR IGNORE INTO user (email, username, password) VALUES("' + email + '","' + username + '","' + password + '");')
        database.commit()

        if cur.lastrowid == 0:
            return redirect(url_for('createuser'))
        else:    
            return redirect(url_for('login'))
    return render_template('CreateUser.html')

@app.route('/createfamily', methods=['GET', 'POST'])
@login_required
def createfamily():
    if request.method == 'POST':
        database = connect('database')
        cur = database.cursor()
        familyname = request.form['familyname']

        cur.execute('INSERT OR IGNORE INTO family (familyname) VALUES("' + familyname +'");')
        database.commit()
        if cur.lastrowid == 0:
            return redirect(url_for('createfamily'))
        else:    
            return redirect(url_for('agenda'))
        return render_template('Agenda.html')
    return render_template('CreateFamily.html')

if __name__ == "__main__":
    app.secret_key = "123"
    app.run(debug=1, host='0.0.0.0')