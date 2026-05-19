# Sa3eedy Voice AI Assistant 🇪🇬🎙️

Real-time Arabic Voice AI web application with a conversational Sa3eedy Egyptian personality using Speech-to-Text, LLMs, and Text-to-Speech.

---

## 🚀 Overview

Sa3eedy Voice AI is an end-to-end Arabic conversational voice assistant that allows users to speak naturally through the browser microphone and receive AI-generated voice replies in a friendly Sa3eedy dialect.

The project combines:

* Real-time voice interaction
* Arabic speech recognition
* Conversational AI
* Arabic text-to-speech synthesis
* Frontend + Backend integration

This is not just a chatbot wrapper — it is a complete Voice AI pipeline.

---

# ✨ Features

* 🎤 Browser microphone recording
* 🗣️ Arabic Speech-to-Text using Faster-Whisper
* 🧠 AI conversation using Gemini API
* 😄 Sa3eedy conversational personality
* 🔊 Arabic Text-to-Speech using Edge TTS
* ⚡ FastAPI backend
* 💬 Conversation history
* 🔄 Automatic audio playback
* 📱 Simple responsive frontend
* 🧩 Modular AI pipeline

---

# 🏗️ Architecture

```text
User Voice
   ↓
Speech To Text (Faster-Whisper)
   ↓
Gemini AI
   ↓
Sa3eedy Reply
   ↓
Text To Speech (Edge TTS)
   ↓
Voice Response
```

---

# 🛠️ Tech Stack

## Backend

* Python
* FastAPI
* Uvicorn

## AI & NLP

* Faster-Whisper
* Gemini API
* Edge TTS

## Frontend

* HTML
* CSS
* JavaScript

---

# 📂 Project Structure

```text
sa3eedy-voice-ai/
│
├── backend/
├── frontend/
├── audio/
├── temp/
├── docs/
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/sa3eedy-voice-ai.git

cd sa3eedy-voice-ai
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

# ▶️ Run The Project

```bash
uvicorn main:app --reload
```

Server will run on:

```text
http://127.0.0.1:8000
```

---

# 🎯 Current Capabilities

✅ Arabic speech recognition
✅ AI-generated Arabic replies
✅ Sa3eedy personality responses
✅ Voice response generation
✅ Full frontend/backend pipeline
✅ Conversational UX flow

---

# 📸 Demo

## Example Conversation

### User

```text
السلام عليكم يا صاحبي عامل ايه؟
```

### AI

```text
وعليكم السلام يا غالي، الدنيا تمام الحمد لله، اخبارك انت ايه؟
```

---

# 🧠 AI Personality

The assistant is designed with a:

* Friendly tone
* Natural Egyptian Arabic
* Light Sa3eedy flavor
* Human-like conversational style
* Simple and understandable responses

---

# 🚧 Future Improvements

* Realtime streaming responses
* WebSockets support
* Lower latency audio pipeline
* Voice interruption handling
* Persistent conversation memory
* Sa3eedy voice cloning
* Better UI/UX
* Mobile optimization

---

# 📈 Challenges Solved

## Gemini Rate Limits

* Switched to Gemini Flash models
* Reduced prompt size
* Added request spacing

## Whisper Accuracy

* Better Arabic configuration
* Improved audio quality
* Fixed language detection

---

# 💼 Portfolio Value

This project demonstrates experience with:

* Voice AI systems
* Arabic NLP
* FastAPI backend development
* Speech processing
* LLM integration
* Real-time conversational systems
* AI product architecture

---

# 🤝 Contributing

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would like to improve.

---

# 📜 License

MIT License

---

# 👨‍💻 Author

Mohamed Abden NourElden

AI Engineer | NLP | Voice AI | Backend AI Systems

* [LinkedIn Profile]([https://www.linkedin.com/in/mhmdaallam/])
* [GitHub Profile](https://github.com/?utm_source=chatgpt.com)
