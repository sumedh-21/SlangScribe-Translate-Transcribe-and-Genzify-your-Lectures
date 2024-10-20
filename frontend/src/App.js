import React, { useState } from "react";
import "./App.css";

const languages = [
  "Chinese",
  "Japanese",
  "Spanish",
  "Hindi",
  "French",
  "German",
  "Arabic",
  "Russian",
];

const App = () => {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState("");
  const [translation, setTranslation] = useState("");
  const [genzifiedText, setGenZifiedText] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [language, setLanguage] = useState("Chinese");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a file.");
      return;
    }

    setIsUploading(true);
    setStatus("Processing your file... Please wait.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log(data.transcription); // Add this line for debugging
      setTranscription(data.transcription);
      setStatus("Processing complete! See the transcription below.");
    } catch (error) {
      console.error("Upload failed:", error);
      setStatus("An error occurred. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleTranslation = async () => {
    if (!transcription) {
      alert("Please transcribe the file first.");
      return;
    }

    setStatus("Translating... Please wait.");

    try {
      const res = await fetch("http://127.0.0.1:5000/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transcription: transcription,
          language: language,
        }),
      });
      const data = await res.json();
      setTranslation(data.translation);
      setStatus("Translation complete! See the result below.");
    } catch (error) {
      console.error("Translation failed:", error);
      setStatus("An error occurred. Please try again.");
    }
  };

  const handleGenZify = async () => {
    if (!transcription) {
      alert("Please transcribe the file first.");
      return;
    }

    setStatus("GenZifying... Please wait.");

    try {
      const res = await fetch("http://127.0.0.1:5000/genzify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: transcription,
        }),
      });
      const data = await res.json();
      setGenZifiedText(data.genzified_text);
      setStatus("GenZification complete! See the result below.");
    } catch (error) {
      console.error("GenZify failed:", error);
      setStatus("An error occurred. Please try again.");
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Transcribe, Translate, And GenZify Your Lectures</h1>
      </header>

      <div className="upload-card">
        <h2>Upload Your Audio File</h2>
        <form onSubmit={handleUpload}>
          <input type="file" onChange={handleFileChange} accept="audio/*" />
          <button type="submit" disabled={isUploading}>
            {isUploading ? "Processing..." : "Upload and Transcribe"}
          </button>
        </form>

        <p className="status-message">{status}</p>

        {transcription && (
          <div className="result-section">
            <h2>Transcription</h2>
            <p>{transcription}</p>

            <h2>Translation</h2>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {languages.map((lang, index) => (
                <option key={index} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
            <button onClick={handleTranslation}>Translate</button>

            {translation && (
              <div>
                <h3>Translation ({language})</h3>
                <p>{translation}</p>
              </div>
            )}

            <h2>GenZify Your Lecture</h2>
            <button onClick={handleGenZify}>GenZify</button>

            {genzifiedText && (
              <div className="genzified-section">
                <h2>GenZified Text</h2>
                <p>{genzifiedText}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
