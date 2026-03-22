from flask import Flask, request, jsonify
import base64, io, urllib.request
from pdf2image import convert_from_bytes
from PIL import Image, ImageChops

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    pdf_url = data.get('pdf_url', '')
    
    # Download PDF
    req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
    pdf_bytes = urllib.request.urlopen(req).read()
    
    # Convert PDF → PNG
    images = convert_from_bytes(pdf_bytes, dpi=150)
    img = images[0]
    
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
    
    # Convert sang base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return jsonify({'png_base64': png_base64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

**Bước 3:** Tạo file `requirements.txt`:
```
flask
pdf2image
Pillow
```

---

**Bước 4:** Tạo file `Procfile`:
```
web: apt-get install -y poppler-utils && python main.py
