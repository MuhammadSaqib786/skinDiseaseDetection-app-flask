# Skin Disease Detection Using CNN

This project is a deep learning web application that detects and classifies skin lesions into 7 categories using a Convolutional Neural Network (CNN). It is built with TensorFlow, Keras, and Flask.

## Features

- Upload skin lesion images for instant classification
- 7 disease categories (e.g., Melanoma, Nevus, BCC)
- User registration and login system (SQLite)
- Real-time prediction with accuracy score
- Simple Flask-based web interface

## Technologies Used

- Python, Flask
- TensorFlow, Keras
- NumPy, OpenCV, PIL
- SQLite (user data)
- HTML, CSS (Bootstrap)

## How to Run

```bash
git clone https://github.com/your-username/skin-disease-detector.git
cd skin-disease-detector
pip install -r requirements.txt
python app.py

Visit http://127.0.0.1:5000 in your browser.

## Model

The CNN model is trained on a Kaggle dataset and saved as Best_Model.h5.
