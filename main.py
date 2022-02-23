from ImageTextReader import image_to_text

import os

for dir_name in os.listdir("images"):
    dir_full = os.path.join("images", dir_name)
    for img_name in os.listdir(dir_full):
        image_to_text(os.path.join(dir_full, img_name),
                      os.path.join("image_texts", img_name.rstrip(".jpeg")+"_text.txt"))
