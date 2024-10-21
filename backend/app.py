from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import whisper
import uuid
from transformers import pipeline
import spacy
from nltk.tokenize import sent_tokenize
import torch
import nltk
nltk.download('punkt')

from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)


if torch.cuda.is_available():
    device = torch.device("cuda")   
else:
    device = torch.device("cpu")
# Load models
whisper_model = whisper.load_model("tiny", device=device)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn",  device=device)
nlp = spacy.load("en_core_web_sm")

# Translation models
translation_pipelines = {
    "Hindi": pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi", device=device),
    "Chinese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh", device=device),
    "Japanese": pipeline("translation", model="Helsinki-NLP/opus-mt-en-jap", device=device),
    "Spanish": pipeline("translation", model="Helsinki-NLP/opus-mt-en-es", device=device),
    "French": pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=device),
    "German": pipeline("translation", model="Helsinki-NLP/opus-mt-en-de", device=device),
    "Arabic": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ar", device=device),
    "Russian": pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru", device=device),
}

UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Transcribe audio using Whisper
def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path)
    return result["text"]

# Summarize the transcription text
def summarize_text(text, max_length=100, min_length=30):
    sentences = sent_tokenize(text)
    chunks = [" ".join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)]
    summary = ""
    for chunk in chunks:
        summarized = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
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

@app.route("/genzify", methods=["POST"])
def genzify():
    data = request.get_json()
    text = data.get("text", "")
    gpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Step 1: Summarize the transcription dynamically based on input length
        sentences = sent_tokenize(text)
        num_sentences = len(sentences)

        # Dynamically adjust summarization limits
        dynamic_max_length = max(40, int(0.5 * num_sentences))  # At least 40 tokens or 50% of input length
        dynamic_min_length = min(20, int(0.2 * num_sentences))  # At least 20 tokens or 20% of input length

        chunks = [" ".join(sentences[i:i + 5]) for i in range(0, num_sentences, 5)]
        summary = ""
        for chunk in chunks:
            summarized = summarizer(chunk, max_length=dynamic_max_length, min_length=dynamic_min_length, do_sample=False)
            summary += summarized[0]["summary_text"] + " "

        slang_prompt = f"Convert this summary into Gen-Z slang using abbreviations, slang words, and no numbers and emojis: {summary}"

        # Step 2: Use GPT-4 API to generate slangified version
        response = gpt_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at summarizing and translating content into Gen-Z slang."},
                {"role": "user", "content": slang_prompt}
            ],
            temperature=0.9,  # Creativity factor
            max_tokens=200  # Dynamic output size
        )

        # print(response)

        slangified_summary = response.choices[0].message.content
        # response.choices[0].message.content

        # Step 3: Return the GenZified summary
        return jsonify({"genzified_text": slangified_summary.strip()})

    except Exception as e:
        return jsonify({"error": f"Error during processing: {str(e)}"}), 500

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
