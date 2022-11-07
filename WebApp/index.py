from flask import Flask
from flask import render_template
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow_addons as tfa
import numpy as np
import PIL
from PIL import Image

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

IMAGE_SIZE = [256, 256]
UPLOAD_FOLDER = './static/photo_jpg'
ALLOWED_EXTENSIONS = { 'jpg', 'jpeg'}
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def decode_jpeg(image_file):
    image = Image.open(image_file)
    image = image.resize((256,256),Image.ANTIALIAS)
    image = np.array(image)
    image = (tf.cast(image, tf.float32) / 127.5) - 1
    image = tf.reshape(image, [1, *IMAGE_SIZE, 3])
    return image

def resize(filename):
    image = Image.open(filename)
    image = image.resize((256,256),Image.ANTIALIAS)
    image.save(str(filename))
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/generate_painting/<filename>")
def generate_painting(filename=None):
    img_path = "./static/photo_jpg/" + str(filename)
    img = decode_jpeg(img_path)
    NEWGEN = tf.keras.models.load_model("./models/MonetGenV4.h5")
    prediction = NEWGEN(img)
    prediction = prediction[0].numpy() * 0.5 + 0.5
    im = PIL.Image.fromarray((prediction * 255).astype(np.uint8))
    path_to_monet = "/generated_monet/Monet-" + str(filename)
    im.save("./static" + path_to_monet)
    resize(img_path)
    return render_template("generated.html", original_photo = str("/photo_jpg/") + filename , path_to_monet=path_to_monet)
    # return render_template(img, test=test)
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('generate_painting', filename=filename))
    return render_template("index.html")