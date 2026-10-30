import pytesseract
from PIL import Image
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    text = pytesseract.image_to_string(Image.open('/app/sample_notebook.jpg'), lang='por')
    print("OCR OUTPUT:")
    print(text)
except Exception as e:
    print("ERROR:", e)
