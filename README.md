---
title: NexusAI
emoji: ✨
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
short_description: AI Assistant with RAG, Web Search & Voice
---

# ✨ NexusAI - Intelligent AI Assistant

A powerful AI chatbot with advanced features:

## 🚀 Features

- **Multi-Provider AI**: Groq (Llama) + Google Gemini
- **RAG (Retrieval-Augmented Generation)**: Upload documents and ask questions
- **Web Search**: Real-time information from the web
- **Voice Input/Output**: Speak to the AI
- **Image Generation**: Create images with Pollinations AI
- **Smart Intent Detection**: Understands typos and context
- **Auto Mode Switching**: Adapts to your question type

## 📋 How to Use

1. **Chat**: Just type your question
2. **Upload Files**: Add PDFs, code, or documents for RAG
3. **Voice**: Click the mic button to speak
4. **Images**: Type "generate image of..." to create images

## ⚙️ Configuration

Add these secrets in your Hugging Face Space settings:
- `GROQ_API_KEY` - Get from [groq.com](https://groq.com)
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com)
- `TAVILY_API_KEY` - (Optional) For web search

## 🛠️ Tech Stack

- Streamlit (Frontend)
- Groq + Gemini (AI Providers)
- FAISS + Sentence Transformers (RAG)
- PySpellChecker (Typo Correction)

---

Built with ❤️ by NexusAI Team
