from flask import Blueprint, request, jsonify
import pytesseract
from PIL import Image
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

    # Validar extensión
    nombre = imagen.filename.lower()
    if not (nombre.endswith(".jpg") or nombre.endswith(".jpeg") or nombre.endswith(".png")):
        return jsonify({"error": "Formato de imagen no permitido. Solo JPG o PNG"}), 400

    try:
        # Validar si realmente es una imagen
        imagen_pil = Image.open(imagen.stream)
        imagen_pil.verify()  # verifica estructura sin decodificar completamente

        imagen.stream.seek(0)
        imagen_pil = Image.open(imagen.stream)

        texto_extraido = pytesseract.image_to_string(imagen_pil, lang="spa")
        return jsonify({"texto": texto_extraido})
    except Exception as e:
        print("Error al procesar imagen:", e)
        return jsonify({"error": "Error al procesar la imagen"}), 500
