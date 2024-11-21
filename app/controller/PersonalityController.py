from flask import request, jsonify
from collections import defaultdict
import logging
import zlib
from app import response
from app.helpers.file_helper import get_sticker_file
import base64



# Data awal
I = ["Cookies Original","Cookies Lotus","Brownies Red Velvet","Brownies Original","Cookies S'mores","Brownies Cheese","Cookies Lotus","Brownies Original"]
S = ["Cookies Original","Cookies Lotus","Cookies S'mores","Brownies Cheese","Cookies S'mores","Brownies Cheese","Cookies Original","Cookies Lotus"]
F = ["Cookies S'mores","Cookies Lotus","Brownies Red Velvet","Brownies Cheese","Cookies Lotus","Brownies Cheese","Brownies Red Velvet","Cookies Lotus","Brownies Red Velvet"]
J = ["Cookies Original","Cookies Lotus","Brownies Original","Cookies Original","Cookies Lotus","Brownies Red Velvet","Brownies Cheese"]
E = ["Cookies S'mores","Brownies Red Velvet","Cookies S'mores","Brownies Cheese","Brownies Red Velvet","Cookies S'mores","Cookies Original","Cookies Lotus","Brownies Red Velvet","Brownies Cheese"]
N = ["Cookies S'mores","Brownies Red Velvet","Brownies Original","Cookies Lotus","Brownies Original","Brownies Red Velvet","Cookies S'mores","Brownies Red Velvet","Brownies Cheese"]
T = ["Cookies Original","Brownies Original","Cookies S'mores","Brownies Original","Cookies S'mores","Cookies S'mores","Cookies Original","Brownies Cheese"]
P = ["Cookies S'mores","Cookies S'mores","Brownies Cheese","Cookies Lotus","Brownies Original","Cookies S'mores","Brownies Cheese","Brownies Red Velvet","Cookies S'mores"]



# Define smaller_than_tree and greater_than_tree
smaller_than_tree = [I, S, F, J]
greater_than_tree = [E, N, T, P]


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

        # Inisialisasi penghitung produk
        product_count = defaultdict(int)

        # Iterasi berdasarkan skor personality
        for i in range(len(personality)):
            if personality[i] >= 3:
                # Ambil data dari mbti[0] (smaller_than_tree)
                for product in mbti[1][i]:
                    product_count[product] += 1
            elif personality[i] >= 1:
                # Ambil data dari mbti[1] (greater_than_tree)
                for product in mbti[0][i]:
                    product_count[product] += 1

        # Menampilkan semua skor di konsol
        # for product, score in product_count.items():
        #     print(f"Product: {product}, Score: {score}")
        
       
        # Mencari produk dengan nilai maksimum
        max_product = max(product_count, key=product_count.get)

        print(f"max product adalah: {max_product}")

                # Menentukan huruf kepribadian
        letters = [] 
        for i, letter in enumerate(["E", "N", "T", "P"]):
            if personality[i] >= 3:
                letters.append(letter)
            else:
                # Pasangannya dari kategori kedua
                letters.append(["I", "S", "F", "J"][i])

        personality_type = "".join(letters)
        print(f"Personality type: {personality_type}")

        index = sticker_index[max_product]


        sticker_path = get_sticker_file(index)
        alias = aliases[max_product]
        description = descriptions["".join(letters)]

        sticker_base64 = encode_image_to_base64(sticker_path)
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


def encode_image_to_base64(file_path, compress=False):
    try:
        with open(file_path, "rb") as img_file:
            # Encode file ke Base64
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')

            if compress:
                # Kompres data Base64 menggunakan zlib
                compressed_data = zlib.compress(base64_data.encode('utf-8'))
                return compressed_data  # Mengembalikan data terkompresi
            else:
                return base64_data  # Mengembalikan data Base64 biasa
    except FileNotFoundError:
        return None

def decompress_base64(compressed_data):
    try:
        # Dekompres data menggunakan zlib
        decompressed_data = zlib.decompress(compressed_data).decode('utf-8')
        return decompressed_data  # Mengembalikan data Base64 asli
    except zlib.error:
        return None
