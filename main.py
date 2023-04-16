import os

from flask import redirect, session, flash

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import cv2
import numpy as np
from PIL import Image
# Create a connection to the database
import sqlite3
# new code above--imports

from flask import Flask, render_template, request, url_for
from keras.models import load_model

# new code below
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              email TEXT,
              gender TEXT,
              phone TEXT,
              password TEXT)''')

conn.commit()

app = Flask(__name__)
app.secret_key = "super_secret_key"

dic = {0: 'Actinic Keratoses', 1: 'Basal Cell Carcinoma', 2: 'Seborrheic Keratosis',
       3: 'Dermatofibroma', 4: 'Malignant Melanoma', 5: 'Melanocytic Nevus', 6: 'Vascular Lesions'}

MODEL_PATH = 'models/Best_Model.h5'
model = load_model(MODEL_PATH)
model.make_predict_function()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_label(img):
    i = img
    p = model.predict_generator(i)
    # now find maximum value from these values
    max, accurate = find_max(p[0])
    return max, accurate


# function to find max
def find_max(data):
    max = 0
    index = 0
    for x in data:
        if x > max:
            max = x
            indexMax = index
        index = index + 1
    return indexMax, max


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'image' not in request.files:
            flash('No file was uploaded.')
            return redirect(request.url)

        file = request.files['image']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No file was uploaded.')
            return redirect(request.url)

        # Check if the file is allowed
        if not allowed_file(file.filename):
            flash('The file type is not allowed.')
            return redirect(request.url)
        img_path = "static/images_saved/" + file.filename
        file.save(img_path)
        # Preprocess image for the model
        img = Image.open(file.stream)

        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, (150, 150))
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)

        # Make prediction
        prediction, acc = predict_label(img)

        acc = acc * 100
        acc = round(acc, 2)
        result = dic[prediction]
        print(acc)

        # Render result template
        return render_template('result.html', result=result, accuracy=acc, image=img_path)

    return render_template('detect.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        gender = request.form['gender']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Insert new user into database
        c.execute('''INSERT INTO users (name, email, gender, phone, password)
                     VALUES (?, ?, ?, ?, ?)''', (name, email, gender, phone, password))
        conn.commit()

        # Redirect to login page
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in database
        c.execute('''SELECT * FROM users
                     WHERE email = ? AND password = ?''',
                  (email, password))
        user = c.fetchone()

        if user:
            # Set session variable and redirect to home page
            session['username'] = user[1]
            return redirect(url_for('home'))

        # Show error message if login fails
        error = 'Invalid username or password'
        flash(error, 'danger')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove the username from the session if it exists
    session.pop('username', None)
    # Redirect to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    # app.debug = True
    app.run(debug=True)
