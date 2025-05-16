# Deploying Telegram-Gemini Chatbot on Render.com

### Overview

This bot listens for messages on Telegram, forwards them to Google’s Gemini model, and relays the AI’s response back to the user. It’s wrapped in a small Flask app providing a /healthz endpoint so it can run as a Web Service on Render.com.

### Github Repository

- **Files to include**  
  - `chatbot.py` — main script
  - `runtimetxt` — pin Python version
  - `requirements.txt` — list dependencies:
    ```txt
    google-generativeai
    requests
    flask
    ```
- **Commit & push** to GitHub repository.

### Configure Environment Variables, Build commnad and Start command

Create environment variables in Render.com project
| Variable         | Value                     |
| ---------------- | ------------------------- |
| `TELEGRAM_TOKEN` | (Telegram bot token)      |
| `GEMINI_KEY`     | (Gemini API key)          |
Build command: `pip install -r requirements.txt`
Start commnad: `python bot.py`

### Result screenshots

| ![Alt Text](/assets/Screenshot_1.jpg) | ![Alt Text]((/assets/Screenshot_2.jpg) | ![Alt Text]((/assets/Screenshot_3.jpg) |
|:-------------------------------------:|:-------------------------------------:|:---------------------------------------:|

<img src="/asset/Screenshot_1.jpg" alt="Image 1" width="200" />  
<img src="path/to/image2.png" alt="Image 2" width="200" />



