import openai
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

chat_ia_bp = Blueprint("chat_ia", __name__)

@chat_ia_bp.route('/chat_ia', methods=["POST"])
def responder():
    data = request.json
    pregunta = data.get("pregunta")
    resumen_usuario = data.get("contexto")

    if not pregunta or not resumen_usuario:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
            {
                "role": "system",
                "content": (
                    "Tu nombre es FinAI. Eres una asistente conversacional amable, profesional y especializada en finanzas personales. "
                    "Puedes responder saludos, agradecimientos, despedidas y mantener una conversación natural. "
                    "Estás diseñada para ayudar con temas como: ahorros, control de gastos, metas financieras, salario y balance mensual. "
                    "Cuando el usuario hace preguntas sobre sus datos, los analizas con lógica clara, porcentajes y consejos. "
                    "Si el usuario menciona temas fuera de la aplicación, responde con respeto que solo puedes ayudar en finanzas personales. "
                    "Responde siempre en español, de manera breve pero útil, con tono humano, positivo, y si aplica, con emojis."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Estos son mis datos financieros:\n{resumen_usuario}\n\n"
                    f"Mensaje: {pregunta}"
                )
            }
        ],
            max_tokens=300,
            temperature=0.7
        )
        contenido = respuesta.choices[0].message.content
        return jsonify({"respuesta": contenido})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error al contactar OpenAI"}), 500
