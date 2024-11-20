import logging
from flask import request 
from app import app
from app.controller import StikerController
from app.controller import PersonalityController
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
    logging.info(f"Received parameters: {request.args}")
    return StikerController.get_sticker_image()

@app.route('/reedem_diskon', methods = ['POST'])
def reedem_diskon():
        return StikerController.reedem_diskon()

@app.route('/personality', methods = ['POST'])
def get_personality():
        return PersonalityController.get_personality()