from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import whisper
import uuid
from transformers import pipeline
import spacy
from nltk.tokenize import sent_tokenize

import nltk
nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# Load models
whisper_model = whisper.load_model("tiny", device="cpu")
summarizer = pipeline("summarization", model="facebook/bart-base")
genzify_pipeline = pipeline("text-generation", model="EleutherAI/gpt-neo-125M",)
nlp = spacy.load("en_core_web_sm")

# Translation models
translation_pipelines = {
    "Hindi": pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi", device="cpu"),
    "Chinese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh", device="cpu"),
    "Japanese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-jap", device="cpu"),
    "Spanish": pipeline("translation", model="Helsinki-NLP/opus-mt-en-es", device="cpu"),
    "French": pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device="cpu"),
    "German": pipeline("translation", model="Helsinki-NLP/opus-mt-en-de", device="cpu"),
    "Arabic": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ar", device="cpu"),
    "Russian": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru", device="cpu"),
}

UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Transcribe audio using Whisper
def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path)
    return result["text"]

# Summarize the transcription text
def summarize_text(text):
    sentences = sent_tokenize(text)
    chunks = [" ".join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)]
    summary = ""
    for chunk in chunks:
        summarized = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        summary += summarized[0]["summary_text"] + " "
    return summary

# Handle file upload and transcription
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    upload_id = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_FOLDER, f"{upload_id}.mp3")
    file.save(file_path)
    
    # Transcribe the audio
    transcription = transcribe_audio(file_path)
    
    return jsonify({"message": "File uploaded successfully", "transcription": transcription})

# Translate transcription text to a specified language
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    transcription = data.get("transcription", "")
    language = data.get("language", "")

    if not transcription or not language:
        return jsonify({"error": "Missing transcription or language"}), 400

    if language not in translation_pipelines:
        return jsonify({"error": f"Translation to {language} is not supported"}), 400
    
    # Perform the translation
    translated_text = translation_pipelines[language](transcription)[0]["translation_text"]
    return jsonify({"translation": translated_text})

# Genzify the text
@app.route("/genzify", methods=["POST"])
def genzify():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Step 1: Summarize the transcription using the summarizer pipeline
        sentences = sent_tokenize(text)
        chunks = [" ".join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)]
        summary = ""
        for chunk in chunks:
            summarized = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
            summary += summarized[0]["summary_text"] + " "
        
        # Step 2: Genzify the summarized text
        slang_prompt = f"Convert this summary into Gen-Z slang: {summary}"

        slangified_summary = genzify_pipeline(
            slang_prompt, 
            max_new_tokens=100,  # Limit to 100 tokens for slangification
            do_sample=True, 
            temperature=0.9,  # Add creativity
            truncation=True  # Ensure the prompt isn't included in the output
        )[0]["generated_text"]

        # Step 3: Return the GenZified summary
        return jsonify({"genzified_text": slangified_summary.strip()})
    
    except Exception as e:
        return jsonify({"error": f"Error during processing: {str(e)}"}), 500





# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
