from flask import request, jsonify
from collections import defaultdict
import logging
from app import response
from app.helpers.file_helper import get_sticker_file
import base64



# Data awal
I = ["Cookies Original","Cookies Lotus","Brownies Original"]
S = ["Cookies Original","Brownies Original","Brownies Red Velvet"]
F = ["Cookies S'mores","Cookies Lotus","Brownies Red Velvet"]
J = ["Cookies Original","Cookies Lotus"]
E = ["Cookies S'mores","Brownies Red Velvet","Brownies Cheese"]
N = ["Cookies S'mores","Cookies Lotus","Brownies Cheese"]
T = ["Cookies Original","Brownies Original","Brownies Cheese"]
P = ["Cookies S'mores","Brownies Original","Brownies Red Velvet","Brownies Cheese"]



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
    "Cookies Original": "lorem ipsum",
    "Cookies S'mores": "loremipsum",
    "Cookies Lotus": "lorem ipsum",
    "Brownies Original": "lorem ipsum",
    "Brownies Red Velvet": "lorem ipsum",
    "Brownies Cheese": "lorem ipsum",
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

        #         # Menentukan huruf kepribadian
        # letters = [] 
        # for i, letter in enumerate(["E", "N", "T", "P"]):
        #     if personality[i] >= 3:
        #         letters.append(letter)
        #     else:
        #         # Pasangannya dari kategori kedua
        #         letters.append(["I", "S", "F", "J"][i])

        # personality_type = "".join(letters)
        # print(f"Personality type: {personality_type}")

        index = sticker_index[max_product]

        
        sticker_path = get_sticker_file(index)
        alias = aliases[max_product]
        description = descriptions[max_product]

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

def encode_image_to_base64(file_path):
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None
