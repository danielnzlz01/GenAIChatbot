from flask import Flask, request, render_template, jsonify
from flask.sessions import SecureCookieSessionInterface
import os
import google.generativeai as genai
import json
from datetime import datetime
import pandas as pd
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, DATA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.session_interface = SecureCookieSessionInterface()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

preguntas_base = [
    "¿En qué universidad estudias?", # 1
    "¿Estás satisfecho con las instalaciones y recursos disponibles en el campus?", # 2
    "¿Te sientes conectado con la comunidad estudiantil?", # 3
    "¿Puedes hacer deporte y jugar con tus amigos en el campus?", # 4
    "¿Puedes socializar y conocer nuevas personas en el campus?", # 5
    "¿Puedes desenvolverte culturalmente en el campus?", # 6
    "¿Las áreas verdes en tu universidad son suficientes y accesibles?", # 7
    "¿Las áreas verdes de tu campus te ayudan a relajarte?", # 8
    "¿Son importantes para tu bienestar y salud mental las áreas verdes?", # 9
    "¿Las áreas verdes en tu campus te permiten convivir con otras personas o descansar?", # 10
    "¿Santa Fe ofrece una buena calidad de vida a los estudiantes?", # 11
    "¿Hay diversas opciones de ocio y entretenimiento en Santa Fe?", # 12
    "¿Puedes organizar partidos o hacer deportes con tus amigos en Santa Fe?", # 13
    "¿Te gustaría que añadieran más áreas verdes y espacios públicos a Santa Fe?", # 14
    "¿Santa Fe te hace sentir que estás en un entorno universitario?", # 15
    "¿Santa Fe ofrece oportunidades para el desarrollo laboral y profesional de los estudiantes?", # 16
    "¿Cuáles son los principales desafíos que enfrentas como estudiante en Santa Fe?", # 17
    "¿Qué tipo de espacios o servicios te gustaría ver más en tu campus o en la zona?", # 18
    "¿Qué elementos de diseño crees que hacen falta para satisfacer tus necesidades culturales, sociales y deportivas?" # 19
]

pregunta_num = 0
end = False
audio = False
respuesta_usuario = ""
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[], temperature=0.5)

@app.route("/", methods=["GET", "POST"])
def encuesta():
    global pregunta_num, respuesta_usuario, chat, end, audio
    if request.method == "POST":
        respuesta_usuario = request.form["respuesta"]
        if not respuesta_usuario.strip() and audio:
            respuesta_usuario = process_audio()
            audio = False
        pregunta_num += 1
    
    if pregunta_num == 0:
        respuesta_usuario = f"init!"
        siguiente_pregunta = llamar_gemini(respuesta_usuario)
    elif pregunta_num < len(preguntas_base):
        siguiente_pregunta = llamar_gemini(respuesta_usuario)
    else:
        end = True
        siguiente_pregunta = llamar_gemini(respuesta_usuario)
        with open('./data/chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(serialize_chat_history(chat.history), f, ensure_ascii=False, indent=4)
        recurring_themes()
        return render_template("encuesta.html", mensaje_final="Gracias por participar en la encuesta!", indice_pregunta=pregunta_num)
    
    return render_template("encuesta.html", pregunta=siguiente_pregunta, indice_pregunta=pregunta_num, audio_y=audio)

def load_audio():
    global audio 

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if f.startswith("recording_") and f.endswith(".mp3")]
    if not files:
        audio = False
        return "No audio files found", 404
    files.sort(key=lambda x: datetime.strptime(x, "recording_%Y-%m-%d_%H-%M-%S-%f.mp3"), reverse=True)
    latest_file = files[0]
    audio = True
    return f"{UPLOAD_FOLDER}/{latest_file}"

@app.route("/load_audio", methods=["POST"])
def load_audio_endpoint():
    global audio
    load_audio()
    return jsonify({"audio_yn": audio}), 200

def process_audio():
    audio_file = genai.upload_file(path=load_audio())
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = "Transcribe the audio file."
    respuesta_audio = model.generate_content([prompt, audio_file])
    return respuesta_audio.text

def llamar_gemini(prompt):
    global model, chat, pregunta_num, end
    if end == False:
        model = genai.GenerativeModel(
            model_name= "gemini-1.5-flash",
            system_instruction= f"""
            Actúa como un chatbot que realiza una encuesta a estudiantes universitarios de la zona Santa Fe en la Ciudad de México. (no menciones que eres un chatbot)
            Si recibes el comando "init!":
            Inicia la conversación basándote en :{preguntas_base[0]}.
            de lo contratario, formula una pregunta más específica y atractiva para el usuario basándote en {preguntas_base[pregunta_num]} (se debe incluir en la pregunta, de manera natural) y la historia del chat.
            """
            )
        chat = model.start_chat(history=chat.history, temperature=0.5)
        response = chat.send_message(prompt)
        return response.text
    else:
        model = genai.GenerativeModel(model_name= "gemini-1.5-flash")
        chat = model.start_chat(history=chat.history, temperature=0.5)
        response = chat.send_message(prompt)
        return response.text

def serialize_chat_history(history):
    return [
        {
            "role": message.role,
            "text": message.parts[0].text
        }
        for message in history
    ]

def build_df(data):
    with io.StringIO(data) as f:
        lines = f.readlines()

    overall_sentiment = int(lines[0].split(":")[1].strip())
    themes = []

    current_sentiment = None
    for line in lines[1:]:
        line = line.strip()
        if line.endswith("themes:"):
            current_sentiment = line[:-8].strip()
        elif line.startswith("-"):
            themes.append({"Sentiment": current_sentiment, "Theme": line[2:].strip()})

    df = pd.DataFrame(themes)
    df = pd.concat([pd.DataFrame({'Sentiment': ['Overall sentiment'], 'Theme': [overall_sentiment]}), df], ignore_index=True)
    df.to_csv("./data/recurring_themes.csv", index=False)
    return df

def recurring_themes():
    model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction= """Your task is to analyze the chat history and identify recurring themes or topics that are relevant to the survey.
                                For this analysis you must only consider the responses when 'role' == 'user' and not when 'role' == 'model'.
                                Pay attention to the context and the questions that are asked to the user.
                                You must provide a summary of the recurring themes and also the overall sentiment of the user regarding 
                                their university being 'introverted' as if they feel connected to their surroundings in the Santa Fe zone in Mexico City.
                                Give your answer in the following format, do NOT write adjectives in the response:
                                Overall sentiment: [numerical value between 1 and 10]
                                Positive (try to get 10 themes, less or none if there's not enough data) themes: [bulletpoints marked with '-' at most 3 words each]
                                Neutral (try to get 10 themes, less or none if there's not enough data) themes: [bulletpoints marked with '-' at most 3 words each]
                                Negative (try to get 10 themes, less or none if there's not enough data) themes: [bulletpoints marked with '-' at most 3 words each]
                                """)
    try:
        chat = model.start_chat(history=chat.history, temperature=0)
        response = chat.send_message("Analyze the chat history. Only consider the responses when 'role' == 'user' and not when 'role' == 'model'.")
        with open('./data/recurring_themes.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        with open('./data/recurring_themes.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        return build_df(data)
    except Exception as e:
        with open('./data/chat_history.json', 'r', encoding='utf-8') as f:
            loaded_chat_history = json.load(f)
        loaded_chat_history = [f"{message['role']}: {message['text']}" for message in loaded_chat_history]
        loaded_chat_history = "\n".join(loaded_chat_history)
        prompt = f"Analyze the chat history. Only consider the responses when 'role' == 'user' and not when 'role' == 'model'. {loaded_chat_history}"
        response = model.generate_content(prompt)
        with open('./data/recurring_themes.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        with open('./data/recurring_themes.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        return build_df(data)

if __name__ == "__main__":
    app.secret_key = os.urandom(24) 
    app.run(debug=True)