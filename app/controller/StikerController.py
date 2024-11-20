from flask import request, jsonify, send_file, url_for
from app import response, uploadconfig, db
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import logging
import os
from io import BytesIO
from app.model.voucher import Voucher
from app.model.record_redemption import Record_Redemption
from PIL import Image, ImageDraw, ImageFont
from app.helpers.file_helper import get_sticker_file


# Jumlah stiker yang dimiliki (misalkan kamu memiliki 10 stiker)
NUM_STICKERS = 6

STICKER_PROBABILITY = [3,3,3,2,2,1]



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


# def get_sticker_image():
#         try:
#             # Menghitung indeks berdasarkan teks
#             code = request.args.get('code')

#             voucher = Voucher.query.filter_by(code=code).first()

#             validate_code = validate_indatabase(voucher)
            
#             if not validate_code["valid"]:
#                 return response.badRequest([], f'Voucher with code {code} : {validate_code["reason"]}')
            
#             index = get_index(code)
#             # Ambil stiker yang sesuai dengan indeks
#             sticker_file = get_sticker_file(index)

#             if not sticker_file:
#                 return response.badRequest([], 'Sticker not found')
            
#             sticker_modify = modify_sticker(sticker_file,code)

#             if not sticker_modify:
#                 return response.badRequest([],'Sticker Failed to generated')
            
#             #update status voucher
#             update_voucher_status(voucher)

#             # kirimkan gambar
#             return sticker_modify
#         except Exception as e:
#             print(e)

import time

def get_sticker_image():
    try:
        start_time = time.time()

        # Langkah 1: Ambil voucher
        code = request.args.get('code')
        voucher_fetch_start = time.time()
        voucher = Voucher.query.filter_by(code=code).first()
        print(f"Waktu mengambil voucher: {time.time() - voucher_fetch_start}s")

        # Langkah 2: Validasi voucher
        validation_start = time.time()
        validate_code = validate_indatabase(voucher)
        print(f"Waktu validasi: {time.time() - validation_start}s")
        if not validate_code["valid"]:
            return response.badRequest([], f'Voucher dengan kode {code}: {validate_code["reason"]}')

        # Langkah 3: Hitung indeks
        index_start = time.time()
        index = get_index(code)
        
        print(f"Waktu menghitung indeks: {time.time() - index_start}s")

        # Langkah 4: Ambil file stiker
        sticker_fetch_start = time.time()
        sticker_file = get_sticker_file(index)
        print(f"Waktu mengambil stiker: {time.time() - sticker_fetch_start}s")
        if not sticker_file:
            return response.badRequest([], 'Stiker tidak ditemukan')

        # Langkah 5: Modifikasi stiker
        sticker_modify_start = time.time()
        sticker_modify = modify_sticker(sticker_file,code)
        print(f"Waktu memodifikasi stiker: {time.time() - sticker_modify_start}s")
        if not sticker_modify:
              return response.badRequest([],'Sticker Failed to generated')

        
        # Langkah 6: Perbarui status voucher
        update_status_start = time.time()
        update_voucher_status(voucher)
        print(f"Waktu memperbarui voucher: {time.time() - update_status_start}s")

        print(f"Total waktu: {time.time() - start_time}s")
        return sticker_modify

    except Exception as e:
        print(e)

def get_index(text):
    total = 0
    for char in text:
        ascii_value = ord(char)
        total = total + ascii_value
    total = total % NUM_STICKERS 
    index = get_sticker_byprobability(total)
    return index

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
            
def reedem_diskon():

    data = request.get_json()
    vouchers = data.get('vouchers')

    if not vouchers:
        return response.badRequest([],"voucher input failed")
    
    missing_voucher = check_voucher(vouchers)

    if len(missing_voucher) != 0:
        return response.badRequest(missing_voucher, "Failed to redeem discount")
    
    update_discount_status(vouchers)

    return response.success([],"Success to redeem discount")
    
def check_voucher(vouchers):
    
    existing_code = Voucher.query.filter(
    Voucher.code.in_(vouchers),
    Voucher.status == True,
    Voucher.discount_status == False).all()
   
    existing_code = [voucher.code for voucher in existing_code] 

    missing_ids = list(set(vouchers) - set(existing_code))
    return missing_ids

def update_discount_status(vouchers):
    try:
        # Update semua voucher yang ada di daftar ke status True
        db.session.query(Voucher).filter(Voucher.code.in_(vouchers)).update(
            {"discount_status": True}, synchronize_session='fetch'
        )
        db.session.commit()  
        return "Vouchers updated successfully"
    except Exception as e:
        db.session.rollback()
        return f"Failed to update vouchers: {str(e)}"
    

def modify_sticker(sticker_file, code):
    try:
        # Open the image
        image = Image.open(sticker_file)

        # Resize the image if it's too large
        image_width, image_height = image.size
        if image_width > 2000 or image_height > 2000:
            image = image.resize((2000, int(2000 * image_height / image_width)))
            image_width, image_height = image.size

        draw = ImageDraw.Draw(image)

        # Desired text dimensions
        max_text_width = int(image_width * 0.8)  # 80% of image width
        max_text_height = int(image_height * 0.1)  # 10% of image height

        # Path to Arial font
        font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"

        # Load font
        font = ImageFont.truetype(font_path, size=max_text_height)

        # Calculate text dimensions
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Adjust font size if needed
        if text_width > max_text_width:
            adjusted_font_size = int(max_text_height * (max_text_width / text_width))
            font = ImageFont.truetype(font_path, size=adjusted_font_size)
            bbox = draw.textbbox((0, 0), code, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        # Calculate text position: center horizontally, 5% margin from bottom
        x_position = (image_width - text_width) / 2
        y_position = int(image_height * 0.03)

        # Draw the text
        draw.text((x_position, y_position), code, fill="black", font=font)

        # Save the modified image to a temporary file buffer
        temp_file = BytesIO()
        image.save(temp_file, format='PNG')
        temp_file.seek(0)

        # Send the modified image
        return send_file(temp_file, mimetype='image/png',download_name=f"{code}.png")

    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_sticker_byprobability(index):
    try:
        records = Record_Redemption.query.all()
  
        sorted_records = sorted(enumerate(records),key=lambda x: (-STICKER_PROBABILITY[x[0]], -x[1].total_redeemed))

        print(f"index awal : {index}")

        newidx = 0

        count_priority = []
        hash_map = {}

        for record in sorted_records:
            if record[1].position == index:
                break
            else:
                newidx = newidx + 1
        
        count = 0
        idxpriority = 0
        for i in range(len(STICKER_PROBABILITY)):
            count = count + sorted_records[i][1].total_redeemed

            if i == len(STICKER_PROBABILITY)-1:
                count_priority.append((STICKER_PROBABILITY[i],count))
                hash_map[STICKER_PROBABILITY[i]] = idxpriority
                break

            if  STICKER_PROBABILITY[i]!= STICKER_PROBABILITY[i+1]:
                count_priority.append((STICKER_PROBABILITY[i],count))
                hash_map[STICKER_PROBABILITY[i]] = idxpriority
                idxpriority = idxpriority + 1
                count = 0
        
        # kita dapat position tapi kita ingin ambil 

        while newidx > 0 :
            priority = STICKER_PROBABILITY[sorted_records[newidx][1].position]
            current_priorityidx = hash_map[priority]

            if current_priorityidx == 0:
                newidx = sorted_records[newidx][1].position
                break
            elif (count_priority[current_priorityidx][1]+1) * count_priority[current_priorityidx-1][0] <= count_priority[current_priorityidx-1][1]:
                newidx = sorted_records[newidx][1].position
                print("quota fulfilled")
                break
            else:
                newidx = newidx - 1

                while newidx > 0 and STICKER_PROBABILITY[newidx] == STICKER_PROBABILITY[newidx+1]:
                    newidx  = newidx -1 
        
        print(f"new index : {newidx}")

        
        Record_Redemption.query.filter_by(position=newidx).update({'total_redeemed': Record_Redemption.total_redeemed + 1})
        db.session.commit()
        return newidx
        
    except Exception as e:
        print(f"get sticker by probability: {e}")


    

    









            


    


