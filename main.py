from flask import Flask, request, jsonify
import base64, io, urllib.request
import fitz  # PyMuPDF
from PIL import Image, ImageChops

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    pdf_url = data.get('pdf_url', '')
    
    req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
    pdf_bytes = urllib.request.urlopen(req).read()
    
    # Convert PDF → PNG bằng PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    mat = fitz.Matrix(2, 2)  # scale 2x cho rõ
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
