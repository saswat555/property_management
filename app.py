from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
app = Flask(__name__)

app.secret_key = 'bandar'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'real estate management'

mysql = MySQL(app)

@app.route('/admin')
def admin_login():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM admin')
    account = cursor.fetchall()
    return render_template('admin.html',data=account)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO client VALUES (null, %s, %s, %s, %s, %s, %s)', ( name ,contact, address, email, username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM property')
        property = cursor.fetchall()
        return render_template('home.html',property=property)
    return redirect(url_for('login'))

@app.route('/view', methods=['GET', 'POST'])
def view():
    property_id=request.form['id']
    session['property_id']= property_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM property WHERE id=%s', (property_id))
    data = cursor.fetchone()
    return render_template('view.html',data=data)
@app.route('/book', methods=['GET', 'POST'])
def book():
    property_id=request.form['id']
    date=request.form['date']
    client_id=session['id']
    print(client_id)
    print(date)
    print(property_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO appointment VALUES (null,%s,%s,%s)', (property_id,date,client_id))
    mysql.connection.commit()
    return redirect( url_for('home'))

@app.route('/')
def first():
    if 'loggedin' in session:
        return redirect('/home')
    else:
        return redirect('/login')
 
   

if __name__ == '__main__':
   app.run()