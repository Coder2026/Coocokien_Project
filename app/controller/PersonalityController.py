from flask import request, jsonify
from PIL import Image
import io
from collections import defaultdict
import logging
import zlib
from app import response
from app.helpers.file_helper import get_sticker_file
import base64


# Define smaller_than_tree and greater_than_tree
smaller_than_tree = ["I", "S", "F", "J"]
greater_than_tree = ["E", "N", "T", "P"]


# Inisialisasi mbti
mbti = [smaller_than_tree, greater_than_tree]

sticker_index = {
    "Cookies Original": 0,
    "Cookies Lotus": 1,
    "Cookies S'mores": 2,
    "Brownies Original": 3,
    "Brownies Red Velvet": 4,
    "Brownies Cheese": 5,
}

aliases = {
    "Cookies Original": "Snick",
    "Cookies Lotus": "Crunch",
    "Cookies S'mores": "Nibbles",
    "Brownies Original": "Mochi",
    "Brownies Red Velvet": "Gooey",
    "Brownies Cheese": "Swirl",
}

product_maping = {
    "ISTJ": "Cookies Original",
    "ISFJ": "Cookies Lotus",
    "INFJ": "Brownies Red Velvet",
    "INTJ": "Brownies Original",
    "ISTP": "Cookies S'mores",
    "ISFP": "Brownies Cheese",
    "INFP": "Cookies Lotus",
    "INTP": "Brownies Original",
    "ESTP": "Cookies S'mores",
    "ESFP": "Brownies Cheese",
    "ENFP": "Cookies S'mores",
    "ENTP": "Brownies Red Velvet",
    "ESTJ": "Cookies Original",
    "ESFJ": "Cookies Lotus",
    "ENFJ": "Brownies Red Velvet",
    "ENTJ": "Brownies Original",
}

descriptions = {
    "ISTJ": "Tertata dan klasik, cocok untuk Anda yang mengutamakan kesederhanaan dan konsistensi. Setiap gigitan penuh dengan kualitas yang tak tergoyahkan.",
    "ISFJ": "Cocok untuk Anda yang perhatian dan penuh dedikasi. Cookies Lotus menghadirkan kenyamanan seperti pelukan hangat yang selalu Anda berikan.",
    "INFJ": "Inspiratif dan memiliki visi besar, Anda adalah seseorang yang membawa perubahan positif. Brownies Red Velvet mencerminkan kedalaman dan keanggunan Anda.",
    "INTJ": "Analitis dan penuh strategi, Brownies Original mencerminkan pendekatan terencana Anda terhadap hidup. Simpel, tapi selalu berkualitas.",
    "ISTP": "Petualang yang selalu mencoba hal baru, Cookies S'mores adalah teman ideal Anda. Kreatif, penuh rasa, dan memberikan kejutan di setiap gigitan.",
    "ISFP": "Artistik dan selalu mengikuti kata hati, Brownies Cheese mencerminkan keindahan dan kesempurnaan di setiap detailnya.",
    "INFP": "Penuh empati dan selalu peduli, Cookies Lotus cocok untuk Anda yang menghargai hubungan mendalam dan harmoni.",
    "INTP": "Anda mencintai logika dan selalu penasaran. Brownies Original adalah pilihan sempurna untuk Anda yang suka memikirkan setiap detail rasa.",
    "ESTP": "Berani dan penuh energi, Cookies S'mores mencerminkan gaya hidup aktif Anda. Manis, penuh rasa, dan selalu menyenangkan.",
    "ESFP": "Pusat perhatian dan selalu membawa kebahagiaan, Brownies Cheese adalah cerminan dari kreativitas dan kebahagiaan yang Anda sebarkan.",
    "ENFP": "Anda selalu membawa ide-ide baru. Cookies S'mores cocok untuk Anda yang selalu penuh kejutan dan inspirasi.",
    "ENTP": "Penuh ide kreatif dan suka berdebat, Brownies Red Velvet mencerminkan keberanian Anda untuk selalu mencoba hal baru.",
    "ESTJ": "Sangat terorganisir dan tegas, Cookies Original mencerminkan kemampuan Anda untuk mengambil tanggung jawab dalam setiap situasi.",
    "ESFJ": "Selalu mendukung orang lain, Cookies Lotus cocok untuk Anda yang suka membawa kebahagiaan bagi orang di sekitar.",
    "ENFJ": "Anda adalah pemimpin yang penuh empati, dan Brownies Red Velvet mencerminkan visi Anda untuk membawa kebaikan bagi semua orang.",
    "ENTJ": "Kuat dan tegas, Brownies Original adalah cerminan dari kepemimpinan Anda yang selalu berorientasi pada hasil."
}



# Fungsi untuk menghasilkan kepribadian berdasarkan skor
def get_personality():
    try:

    
        # Mendapatkan data dari request
        data = request.get_json()
        personality = data.get('score')  # Skor input dari user, berupa list


        # Validasi data input
        if not isinstance(personality, list) or len(personality) != len(mbti[0]):
            return response.badRequest([],"error: Invalid score input")
        
        hasil_mbti = ""
        # Iterasi berdasarkan skor personality
        for i in range(len(personality)):
            if personality[i] >= 3:
                hasil_mbti+=mbti[1][i]
            elif personality[i] >= 1:
                hasil_mbti+=mbti[0][i]

       

        product = product_maping[hasil_mbti]
        index = sticker_index[product]
        sticker_path = get_sticker_file(index)
        alias = aliases[product]
        description = descriptions[hasil_mbti]

       
        sticker_base64 = encode_image_to_base64_with_compression(sticker_path, quality=30)
        if not sticker_base64:
            return response.badRequest([], "sticker not found")
        if not sticker_base64:
            return response.badRequest([],"sticker not found")


        data = {
            "product": product,
            "alias": alias,
            "description": description,
            "sticker_base64": sticker_base64
        }

        return response.success(data, "Data retrieved successfully")


    except Exception as e:
        logging.error(f"Error in generate_personality: {e}")
        print("Error in generate_personality: {e}")


def encode_image_to_base64_with_compression(file_path, quality=25, compress_base64=False):
    """
    Kompres gambar dengan Pillow dan encode ke Base64.
    
    Args:
        file_path (str): Path ke file gambar asli.
        quality (int): Kualitas kompresi (1-100).
        compress_base64 (bool): Jika True, kompres string Base64 dengan zlib.

    Returns:
        str: Gambar dalam format Base64 yang sudah dikompresi.
    """
    try:
        # Buka gambar menggunakan Pillow
        with Image.open(file_path) as img:
            # Konversi gambar ke RGB jika tidak dalam format RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Kompres gambar menggunakan kualitas tertentu
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", optimize=True, quality=quality)
            buffer.seek(0)

            # Encode gambar terkompresi ke Base64
            base64_data = base64.b64encode(buffer.read()).decode("utf-8")

            # Kompres string Base64 jika diminta
            if compress_base64:
                compressed_data = zlib.compress(base64_data.encode("utf-8"))
                return compressed_data

            return base64_data
    except FileNotFoundError:
        print(f"File tidak ditemukan: {file_path}")
        return None
    except Exception as e:
        print(f"Error saat encode dan kompres gambar: {e}")
        return None
