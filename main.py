import pytesseract transformers pandas
from PIL import Image

image = Image.open('receipt.png')
text = pytesseract.image_to_string(image)
print(text)

