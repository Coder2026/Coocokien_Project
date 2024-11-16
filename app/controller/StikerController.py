from flask import request, jsonify, send_file, url_for
from app import response, uploadconfig, db
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import logging
import os
from app.model.voucher import Voucher

# Jumlah stiker yang dimiliki (misalkan kamu memiliki 10 stiker)
NUM_STICKERS = 6

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STICKER_DIR = os.path.join(BASE_DIR, '..', '..', 'stickers')


def upload_image():
    try:
        if 'image' not in request.files:
            return response.badRequest([], 'file not found')
        
        image_file = request.files['image']
        if image_file.filename == '':
            return response.badRequest([], 'invalid image')
        
        if not image_file and not uploadconfig.allowed_file(image_file.filename):
            return response.badRequest([], 'file not allowed')
        
        code = generate_code(image_file)

        return response.success(code,"successful code converted")
    
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
  
        # Hapus file gambar sementara
        os.remove(image_path)
        
        return code

    except Exception as e:
        print(e)


def get_sticker_image():
        try:
            # Menghitung indeks berdasarkan teks
            code = request.args.get('code')

            

            voucher = Voucher.query.filter_by(code=code).first()

            validate_code = validate_indatabase(voucher)
            
            if not validate_code["valid"]:
                return response.badRequest([], f'Voucher with code {code} : {validate_code["reason"]}')
            
            index = get_index(code)
            # Ambil stiker yang sesuai dengan indeks
            sticker_file = get_sticker_file(index)

            if not sticker_file:
                return response.badRequest([], 'Sticker not found')
            
            #update status voucher
            update_voucher_status(voucher)

            # kirimkan gambar
            return sticker_file
        except Exception as e:
            print(e)

def get_index(text):
    total = 0
    for char in text:
        ascii_value = ord(char)
        total = total + ascii_value
    total = total % NUM_STICKERS 
    return total

def update_voucher_status(voucher):
    try:
        voucher.status = True
        db.session.commit()
        logging.info(f"Voucher {voucher.code} status updated to redeemed")
    except Exception as e:
        logging.error(f"Error updating voucher status: {e}")
        raise

def validate_indatabase(voucher):
    try:
       
        # Jika kode tidak ditemukan
        if not voucher:
            return {"valid": False, "reason": "not_found"}

        # Jika kode sudah digunakan
        if voucher.status == 1:
            return {"valid": False, "reason": "already_redeemed"}

        # Jika kode valid
        return {"valid": True, "voucher": voucher}
    except Exception as e:
        print("Error:", e)
        return {"valid": False, "reason": "error"}
            
def get_sticker_file(index):
    sticker_path = os.path.join(STICKER_DIR, f'sticker_{index}.jpg')

    logging.info(f"Checking if sticker file exists at: {sticker_path}")
    if os.path.exists(sticker_path):
        return send_file(sticker_path, mimetype='image/jpeg') 
    else: 
        return None
    

def redem_diskon():

    data = request.get_json()
    vouchers = data.get('vouchers')

    if not vouchers:
        return response.badRequest([],"voucher input failed")
    
    missing_voucher = check_voucher(vouchers)

    if len(missing_voucher) != 0:
        return response.badRequest(missing_voucher, "Failed to redeem discount")
    

    return response.success([],"Success to redeem discount")
    
def check_voucher(vouchers):
    
    existing_code = Voucher.query(Voucher.id).filter(Voucher.code.in_(vouchers)).all()
    existing_code = [code[0] for code in existing_code]  # Konversi hasil query ke list

    # Cari ID yang tidak ada
    missing_ids = list(set(vouchers) - set(existing_code))

    return missing_ids

def update_discount_status(vouchers):
    try:
        # Update semua voucher yang ada di daftar ke status True
        db.session.query(Voucher).filter(Voucher.code.in_(vouchers)).update(
            {"discount_status": True}, synchronize_session='fetch'
        )
        db.session.commit()  
        return f"Updated {len(vouchers)} vouchers to discount status True."
    except Exception as e:
        db.session.rollback()
        return f"Failed to update vouchers: {str(e)}"
    

