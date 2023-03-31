from flask import Flask, render_template, request, redirect, url_for, session
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


def predict_label(img_path):
    i = image.load_img(img_path, target_size=(150, 150))
    i = image.img_to_array(i) / 255.0
    i = i.reshape(1, 150, 150, 3)
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
        # Code to detect skin disease
        return render_template('result.html')
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
