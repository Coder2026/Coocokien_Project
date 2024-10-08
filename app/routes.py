from app import app
from app.controller import StikerController
from flask_cors import CORS
CORS(app)


@app.route('/')
def index():
    return "Hello, User!"

@app.route('/upload',methods = ['POST'])
def upload_image():
    return StikerController.upload_image()

@app.route('/sticker/<filename>', methods=['GET'])
def download_sticker(filename):
    return StikerController.download_sticker(filename)

   