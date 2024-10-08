from flask import request, jsonify, send_file, url_for
from app import response, uploadconfig, db
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import os
from app.model.voucher import Voucher

# Jumlah stiker yang dimiliki (misalkan kamu memiliki 10 stiker)
NUM_STICKERS = 6

STICKER_DIR = os.path.abspath(os.path.join(os.getcwd(), 'stickers'))

def upload_image():
    try:
        if 'image' not in request.files:
            return response.badRequest([], 'file not found')
        
        image_file = request.files['image']
        if image_file.filename == '':
            return response.badRequest([], 'invalid image')
        
        if not image_file and not uploadconfig.allowed_file(image_file.filename):
            return response.badRequest([], 'file not allowed')
        
        return generate_code(image_file)
    
    except Exception as e:
        print(e)
        return response.error('An error occurred during upload')

def generate_code(image_file):
    try:
        # Buat direktori untuk menyimpan file sementara
        if not os.path.exists('uploaded_images'):
            os.makedirs('uploaded_images')

        # Simpan file gambar sementara
        image_path = os.path.join('uploaded_images', secure_filename(image_file.filename))
        image_file.save(image_path)

        # Membaca gambar dengan OpenCV
        image = cv2.imread(image_path)

        # Konversi gambar ke grayscale untuk meningkatkan akurasi OCR
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Menerapkan thresholding untuk meningkatkan kontras
        _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

        # Melakukan OCR menggunakan pytesseract untuk mengekstrak teks
        code = pytesseract.image_to_string(thresh_image)
        code = str(code)
    
        if not validate_indatabase(code):
            return response.badRequest([], f"Voucher with code {code} not found")

        # Menghitung indeks berdasarkan teks
        index = get_index(code)
        
        # Ambil stiker yang sesuai dengan indeks
        sticker_file = get_sticker_file(index)
        print(sticker_file)

        if not sticker_file:
            return response.badRequest([], 'Sticker not found')

        # Hapus file gambar sementara
        os.remove(image_path)

        # kirimkan gambar
        return get_sticker_file(index)
    
    except Exception as e:
        print(e)

def get_index(text):
    total = 0
    for char in text:
        ascii_value = ord(char)
        total = total + ascii_value
    total = total % NUM_STICKERS 
    return total

def validate_indatabase(code):
    try:
        voucher = Voucher.query.filter(Voucher.code == code)
        if not voucher:
            return False
        return True
    except Exception as e:
        print(e)
            
def get_sticker_file(index):
    sticker_path = os.path.join(STICKER_DIR, f'sticker_{index}.jpg')
    if os.path.exists(sticker_path):
        return send_file(sticker_path, mimetype='image/jpeg') 
    else: 
        return response.badRequest([], 'Sticker not found')