from flask import Blueprint, request, jsonify
import pytesseract
from PIL import Image
import io
import os

# Ruta para Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\ocr\tesseract.exe"

# Ruta al directorio donde están los idiomas
os.environ["TESSDATA_PREFIX"] = r"C:\ocr\tessdata"
ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route("/api/leer_boleta", methods=["POST"])
def leer_boleta():
    if "imagen" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400

    imagen = request.files["imagen"]
    
    try:
        imagen_pil = Image.open(imagen.stream)
        texto_extraido = pytesseract.image_to_string(imagen_pil, lang="spa")  # español
        return jsonify({"texto": texto_extraido})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
