from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)


app.secret_key = 'xyz'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythondb'


mysql = MySQL(app)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM uzytkownicy WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Nieprawidłowy login lub hasło!'
    return render_template('index.html', msg=msg)

@app.route('/login/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM uzytkownicy WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Takie konto już istnieje!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Nieprawidłowy adres email!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Nazwa użytkownika może zawierać tylko litery i cyfry!'
        elif not username or not password or not email:
            msg = 'Uzupełnij wszystkie pola!'
        else:
            cursor.execute('INSERT INTO uzytkownicy VALUES (NULL, %s, %s, %s)', (username, email, password,))
            mysql.connection.commit()
            msg = 'Zarejestrowałeś się!'
    elif request.method == 'POST':
        msg = 'Uzupełnij wszystkie pola!'

    return render_template('register.html', msg=msg)

@app.route('/login/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))
