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

@app.route('/sticker', methods=['POST'])
def upload_code():
    return StikerController.get_sticker_image()

@app.route('/reedem_diskon', methods = ['POST'])
def reedem_diskon():
        return StikerController.reedem_diskon()

   