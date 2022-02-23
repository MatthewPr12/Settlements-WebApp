import pytesseract
import cv2


def read_image(image):
    img = cv2.imread(image)

    text = pytesseract.image_to_string(img, lang="ukr")
    with open(image, 'w', encoding='utf-8') as file:
        file.write(text)
