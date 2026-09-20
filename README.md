# AI Language Translator

**CodeAlpha – Artificial Intelligence Internship · Task 1**

A clean, modern web application that translates text between 13+ languages.
The user types text, picks a source and target language, and the Flask backend
calls a translation API and returns the translated text as JSON.

---

## Features

- Large text input with a live **character counter** and **Clear** button
- **Source** and **Target** language dropdowns (English, Hindi, Spanish, French,
  German, Chinese, Japanese, Korean, Arabic, Russian, Portuguese, Italian, Bengali)
- **Swap Languages** button
- **Translate** button with a loading spinner
- Clear, readable **output box** for the translation
- **Copy** button with a small "Copied!" confirmation
- **Listen (Text-to-Speech)** using the browser SpeechSynthesis API
- Full validation: empty input, identical languages, invalid languages
- Friendly error messages for API failures, network errors and server errors
- Responsive design for desktop, tablet and mobile
- API key stored safely in a `.env` file — never exposed to the browser

---

## Technologies Used

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask |
| Translation | Google Cloud Translation API (v2), with MyMemory as a free fallback |
| Config | python-dotenv (`.env` environment variables) |
| HTTP | requests |

---

## How the Application Works

1. The user enters text and selects the source and target languages.
2. JavaScript validates the input (no empty text, languages must differ).
3. JavaScript sends a `POST` request to `/translate` with JSON:
   `{ "text": "...", "source": "en", "target": "hi" }`
4. Flask validates the data again on the server.
5. Flask calls the translation API using the key from `.env`.
6. Flask returns `{ "translated_text": "..." }`.
7. JavaScript displays the translation, and enables **Copy** and **Listen**.

---

## Installation (Windows)

### 1. Get the project
```bash
git clone https://github.com/<your-username>/AI-Language-Translator.git
cd AI-Language-Translator
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file
Copy the example file and rename it:
```bash
copy .env.example .env
```
Then open `.env` in a text editor and paste your key:
```
GOOGLE_TRANSLATE_API_KEY=your_real_key_here
FLASK_DEBUG=True
PORT=5000
```

> **Where do I get the key?**
> Go to <https://console.cloud.google.com/> → create a project →
> enable **Cloud Translation API** → *APIs & Services → Credentials →
> Create credentials → API key* → copy the key into `.env`.
>
> **No key yet?** Leave `GOOGLE_TRANSLATE_API_KEY` empty. The app then
> automatically uses the free **MyMemory** API so you can still test everything.

### 5. Run the application
```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## How to Test the Translator

1. Open http://127.0.0.1:5000
2. Type `Hello, how are you?` in the input box.
3. Source = **English**, Target = **Hindi**.
4. Click **Translate** → the Hindi translation appears on the right.
5. Click **Copy** → the "Copied!" message appears, paste it anywhere.
6. Click **🔊 Listen** → the browser reads the translation out loud.
7. Click **Swap** → languages switch, the translation moves to the input.
8. Click **Translate** with an empty box → you see a validation error.
9. Visit http://127.0.0.1:5000/health → confirms the server and provider.

Test the API directly (PowerShell):
```powershell
curl -X POST http://127.0.0.1:5000/translate ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Good morning\",\"source\":\"en\",\"target\":\"fr\"}"
```

---

## API Information

### `POST /translate`

**Request**
```json
{ "text": "Hello", "source": "en", "target": "hi" }
```

**Success response — 200**
```json
{ "translated_text": "नमस्ते", "source": "en", "target": "hi" }
```

**Error response — 400 / 502 / 504 / 500**
```json
{ "error": "Please enter some text to translate." }
```

### `GET /health`
```json
{ "status": "ok", "provider": "google" }
```

### Supported language codes
`auto` (detect), `en`, `hi`, `es`, `fr`, `de`, `zh`, `ja`, `ko`, `ar`, `ru`, `pt`, `it`, `bn`

---

## Project Structure

```
AI-Language-Translator/
│
├── app.py                 # Flask backend + /translate endpoint
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Keeps .env and venv out of Git
├── README.md              # This file
│
├── templates/
│   └── index.html         # Translator page
│
├── static/
│   ├── css/
│   │   └── style.css      # Styling and responsive layout
│   └── js/
│       └── script.js      # Validation, API calls, copy, text-to-speech
│
└── screenshots/           # Add your app screenshots here
```

---

## Screenshots

Place your images inside the `screenshots/` folder and they will show up here.

| Home page | Translation result |
|-----------|--------------------|
| ![Home](screenshots/home.png) | ![Result](screenshots/result.png) |

---

## Security Notes

- The API key is read from `.env` using `python-dotenv`.
- `.env` is listed in `.gitignore`, so it is never pushed to GitHub.
- The key is used **only** inside `app.py` — the browser never sees it.
- All input is validated on both the client and the server.

---

## Future Improvements

- Automatic language detection display
- Translation history saved in a database
- File upload (.txt / .pdf) translation
- Voice input using the Web Speech Recognition API
- Light / dark theme toggle
- Deployment to Render or Railway

---

## Author

Built as part of the **CodeAlpha Artificial Intelligence Internship – Task 1**.
