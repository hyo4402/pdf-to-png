from flask import Flask, request, jsonify
import base64, io, requests
import fitz
from PIL import Image, ImageChops

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    pdf_url = data.get('pdf_url', '')
    
    # Fix Google Drive URL để download trực tiếp
    if 'drive.google.com' in pdf_url:
        file_id = pdf_url.split('/d/')[1].split('/')[0]
        pdf_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    # Download PDF
    r = requests.get(pdf_url, allow_redirects=True)
    pdf_bytes = r.content
    
    # Convert PDF → PNG
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Auto crop phần trắng thừa
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        padding = 20
        img = img.crop((
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(img.width,  bbox[2] + padding),
            min(img.height, bbox[3] + padding)
        ))
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return jsonify({'png_base64': png_base64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

Thêm `requests` vào `requirements.txt`:
```
flask
PyMuPDF
Pillow
requests
