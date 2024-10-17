from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import whisper
import uuid
from transformers import pipeline
import spacy
from nltk.tokenize import sent_tokenize
import nltk
import os
from dotenv import load_dotenv
import torch  


# Load environment variables
load_dotenv()

# Retrieve tokens from environment variables
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

nltk.download('punkt')

UPLOAD_FOLDER = "backend/uploads"
TRANSCRIPT_FOLDER = "backend/transcripts"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# Load models
whisper_model = whisper.load_model("tiny")
summarizer = pipeline("summarization", model="facebook/bart-base")
nlp = spacy.load("en_core_web_sm")

# Translation pipelines
device = 0 if torch.cuda.is_available() else -1

translation_pipelines = {
    "Hindi": pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi", device= device, use_auth_token=huggingface_token),
    "Chinese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh", device=device, use_auth_token=huggingface_token),
    "Japanese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-jap", device=device, use_auth_token=huggingface_token),
    "Spanish": pipeline("translation", model="Helsinki-NLP/opus-mt-en-es", device=device, use_auth_token=huggingface_token),
    "French": pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=device, use_auth_token=huggingface_token),
    "German": pipeline("translation", model="Helsinki-NLP/opus-mt-en-de", device=device, use_auth_token=huggingface_token),
    "Arabic": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ar", device=device, use_auth_token=huggingface_token),
    "Portuguese": pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt", device=device, use_auth_token=huggingface_token),
    "Russian": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru", device=device, use_auth_token=huggingface_token),
}

def transcribe_audio(file_path):
    """Transcribe audio using Whisper."""
    result = whisper_model.transcribe(file_path)
    return result["text"]

def summarize_text(text):
    """Summarize the transcription."""
    sentences = sent_tokenize(text)
    chunks = [" ".join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)]
    summary = ""
    for chunk in chunks:
        summarized = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        summary += summarized[0]["summary_text"] + " "
    return summary

def extract_topics(text):
    """Extract key topics using spaCy."""
    doc = nlp(text)
    topics = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART"]]
    return list(set(topics))

def generate_quiz(topics):
    """Generate quiz questions based on topics."""
    questions = []
    for topic in topics:
        question = f"What do you know about {topic}?"
        options = [f"{topic} is important.", f"{topic} is not relevant.", f"Nothing is known about {topic}."]
        questions.append({
            "question": question,
            "options": options,
            "answer": options[0]
        })
    return questions

def translate_text(text, target_language):
    """Translate text into the selected language."""
    if target_language in translation_pipelines:
        translation = translation_pipelines[target_language](text)[0]["translation_text"]
        return translation
    else:
        return f"Translation to {target_language} is not supported."
    
genzify_pipeline = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

def genzify_with_gpt(text, style):
    """Rewrite the given text in a Gen Z style with a custom prompt."""
    prompt = f"Rewrite the following lecture in a {style} Gen Z way: {text}"
    result = genzify_pipeline(prompt, max_length=200)[0]["generated_text"]
    return result

@app.route("/genzify", methods=["POST"])
def genzify():
    """Endpoint to GenZify a given text."""
    data = request.get_json()
    text = data.get("text", "")
    style = data.get("style", "quirky")  

    if not text:
        return jsonify({"error": "No text provided"}), 400

    genzified_text = genzify_with_gpt(text, style)
    return jsonify({"genzified_text": genzified_text})

@app.route("/upload", methods=["POST"])
def upload_file():
    """Upload and process audio files."""
    if "file" not in request.files or "language" not in request.form:
        return jsonify({"error": "Missing file or language"}), 400

    file = request.files["file"]
    language = request.form["language"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    upload_id = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_FOLDER, f"{upload_id}.mp3")
    file.save(file_path)

    transcription = transcribe_audio(file_path)
    summary = summarize_text(transcription)
    topics = extract_topics(transcription)
    quiz = generate_quiz(topics)
    translation = translate_text(transcription, language)

    transcript_path = os.path.join(TRANSCRIPT_FOLDER, f"{upload_id}.txt")
    with open(transcript_path, "w") as f:
        f.write(transcription)

    return jsonify({
        "transcription": transcription,
        "summary": summary,
        "topics": topics,
        "quiz": quiz,
        "translation": translation,
        "language": language
    })

@app.route("/transcripts/<path:filename>", methods=["GET"])
def download_transcript(filename):
    """Download the transcript."""
    return send_from_directory(TRANSCRIPT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)

