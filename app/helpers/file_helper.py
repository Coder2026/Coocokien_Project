import logging
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STICKER_DIR = os.path.join(BASE_DIR, '..', '..', 'stickers')


def get_sticker_file(index):
    sticker_path = os.path.join(STICKER_DIR, f'sticker_{index}.jpg')

    logging.info(f"Checking if sticker file exists at: {sticker_path}")
    if os.path.exists(sticker_path):
        return sticker_path
    else: 
        return None