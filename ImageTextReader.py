# ****************************
# 
# No need to get this module working, all images have already been converted to text in image_texts folder
# 
# ****************************

import pytesseract
import cv2


def image_to_text(read_path, save_path):
    img = cv2.imread(read_path)

    tessdata_dir_config = r'--tessdata-dir "/home/oleg/share/tessdata"'
    text = pytesseract.image_to_string(
        img, lang="ukr", config=tessdata_dir_config)
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(text)

