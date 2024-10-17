import React, { useState } from "react";
import "./App.css";

const languages = [
  "Chinese", "Japanese", "Spanish", "Hindi",
  "French", "German", "Arabic",
  "Portuguese", "Russian"
];

const App = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("Chinese");
  const [response, setResponse] = useState(null);
  const [genzifiedText, setGenzifiedText] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [stylePrompt, setStylePrompt] = useState("cool");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleLanguageChange = (e) => setLanguage(e.target.value);

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
    formData.append("language", language);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResponse(data);
      setStatus("Processing complete! See the results below.");
    } catch (error) {
      console.error("Upload failed:", error);
      setStatus("An error occurred. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenZify = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/genzify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: response.transcription,
          style: stylePrompt,
        }),
      });
      const data = await res.json();
      setGenzifiedText(data.genzified_text);
    } catch (error) {
      console.error("GenZify failed:", error);
      alert("GenZify failed.");
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>T4: Transcribe, Test, Translate, and Trim</h1>
      </header>

      <div className="upload-card">
        <h2>Upload Your Audio File</h2>
        <form onSubmit={handleUpload}>
          <input type="file" onChange={handleFileChange} accept="audio/*" />
          <select value={language} onChange={handleLanguageChange}>
            {languages.map((lang, index) => (
              <option key={index} value={lang}>
                {lang}
              </option>
            ))}
          </select>
          <button type="submit" disabled={isUploading}>
            {isUploading ? "Processing..." : "Upload and Transcribe"}
          </button>
        </form>

        <p className="status-message">{status}</p>

        {response && (
          <div className="result-section">
            <h2>Transcription</h2>
            <p>{response.transcription}</p>

            <h2>Summary (Trim)</h2>
            <p>{response.summary}</p>

            <h2>Key Topics</h2>
            <ul>
              {response.topics.map((topic, index) => (
                <li key={index}>{topic}</li>
              ))}
            </ul>

            <h2>Translation ({response.language})</h2>
            <p>{response.translation}</p>

            <h2>Quiz</h2>
            {response.quiz.map((q, index) => (
              <div key={index} className="quiz-section">
                <p>{q.question}</p>
                <ul>
                  {q.options.map((option, i) => (
                    <li key={i}>{option}</li>
                  ))}
                </ul>
              </div>
            ))}

            <h2>GenZify Your Lecture</h2>
            <input
              type="text"
              value={stylePrompt}
              onChange={(e) => setStylePrompt(e.target.value)}
              placeholder="Enter a style (e.g., funny, cool)"
            />
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
