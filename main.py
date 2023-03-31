from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from tensorflow import keras
import cv2
import numpy as np
from PIL import Image
# Create a connection to the database
import sqlite3
# new code above--imports
from pathlib import Path
from os import path

from flask import Flask, render_template, request
from keras.models import load_model
from keras.preprocessing import image

# new code below
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT,
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
        username = request.form['username']
        password = request.form['password']

        # Insert new user into database
        c.execute('''INSERT INTO users (username, password)
                     VALUES (?, ?)''', (username, password))
        conn.commit()

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in database
        c.execute('''SELECT * FROM users
                     WHERE username = ? AND password = ?''',
                  (username, password))
        user = c.fetchone()

        if user:
            # Set session variable and redirect to home page
            session['username'] = user[1]
            return redirect(url_for('home'))

        # Show error message if login fails
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

    return render_template('login.html')


if __name__ == '__main__':
    # app.debug = True
    app.run(debug=True)
