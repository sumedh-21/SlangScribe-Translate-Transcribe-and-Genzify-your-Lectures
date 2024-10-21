# SlangScribe: Transcribe,Translate and Genzify Your Lectures

SlangScribe is a web application designed to transcribe audio files, summarize the transcriptions, translate them into multiple languages, and even "Genzify" the content into Gen-Z slang for added fun! It uses OpenAI's GPT-4 for high-quality text generation and summarization, Whisper for transcription, and Hugging Face pipelines for translation.

<div align="center">
  <a href="https://youtu.be/tu6YVaFL6Ps">
    <img src="https://img.youtube.com/vi/tu6YVaFL6Ps/0.jpg" alt="SlangScribe Video" style="width:70%, height:50%;">
  </a>
  <br>
  <p>Click the image above to watch the demo on YouTube.</p>
</div>

# Features
* Audio Transcription: Uses OpenAI's Whisper model to convert audio files (.mp3, .mp4, .mp4a or .wav format for best use) to text.
* Translation: Translates the text into multiple languages, including Hindi, Chinese, Japanese, Spanish, French, and more.
* Summarization: Summarizes the transcription using the Hugging Face summarization pipeline.
* Gen-Z Slang Conversion: Converts the summarized text into a Gen-Z style summary using OpenAI GPT-4 API.
* Flask API: Exposes various API endpoints for uploading files, translating text, summarizing content, and Gen-Zifying text.

# Installation and Setup
1. Clone the Repository
```
git clone https://github.com/your-username/t4genz.git
cd t4genz
```

2. Backend Setup
Create a virtual environment:
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```
Install the required packages:
``` 
pip install -r requirements.txt
```
Set Environment Variables: Create a .env file with the following contents:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```
Run the Flask backend:
```
flask run --host=0.0.0.0 --port=5000 
```

3. Frontend Setup
Navigate to the frontend/ directory:
```
cd frontend
```
Install dependencies:
``` 
npm install
```
Run the frontend:
``` 
npm start
```

# API Endpoints

## `/upload`
**Request:**  
- **file**: Audio file to transcribe.  
- **language**: (Optional) Target translation language.  

**Response:**  
- Transcription and optional translation result.

---

## `/translate`
**Request:**  
- **transcription**: Text to translate.  
- **language**: Target language.

**Response:**  
- Translated text.

---

## `/genzify`
**Request:**  
- **text**: Text to convert into Gen-Z slang.  

**Response:**  
- Gen-Z slang version of the text.


# License
* This project is licensed under the MIT License. See the LICENSE file for details.



