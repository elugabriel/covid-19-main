from flask import Flask, render_template, url_for, flash, redirect, request
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np
import sqlite3
import bcrypt


app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))

# Database connection
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (firstname TEXT, lastname TEXT, username TEXT, email TEXT, address TEXT, password TEXT)')
conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Encode the user input password

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        stored_password = user[5].encode('utf-8') if user and user[5] else None  # Encode the stored password from the database

        conn.close()

        if stored_password and bcrypt.checkpw(password, stored_password):
            stored_username = user[2]
            # session['username'] = stored_username
            return render_template('index.html')
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        address = request.form['address']
        
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            username TEXT,
            email TEXT,
            address TEXT,
            ssname TEXT,
            purpose TEXT,
            password TEXT
        )''')
        conn.commit()

        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        else:
            cur.execute('INSERT INTO users (firstname, lastname, username, email, address,  password) VALUES (?, ?, ?, ?, ?, ?)', (firstname, lastname, username, email, address, hashed_password))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))

    return render_template('signup.html')


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    total_case = request.form.get("total_case")
    
    num = int(total_case)
    from sklearn.preprocessing import PolynomialFeatures
    poly_reg = PolynomialFeatures(degree = 3)
    
    
    prediction = model.predict(poly_reg.fit_transform([[num]]))
    prediction = np.asarray(prediction, dtype = 'int')

    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)