"""
AI Language Translator - Flask backend
CodeAlpha Artificial Intelligence Internship - Task 1

This file:
  1. Serves the front-end page (templates/index.html)
  2. Exposes POST /translate which calls a translation API and returns JSON

The API key is NEVER hard-coded. It is read from the .env file.
"""

import os
import html
import requests

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load variables written inside the .env file into the environment
load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Google Cloud Translation API key (optional but recommended).
GOOGLE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()

GOOGLE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

# Free fallback API (no key needed). Used only when no Google key is present,
# so that the project still works out of the box for testing.
MYMEMORY_ENDPOINT = "https://api.mymemory.translated.net/get"

# Languages the UI supports. Keep this in sync with the dropdowns in index.html
SUPPORTED_LANGUAGES = {
    "auto": "Detect language",
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "bn": "Bengali",
}

MAX_TEXT_LENGTH = 5000


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the translator page."""
    return render_template("index.html", languages=SUPPORTED_LANGUAGES)


@app.route("/health")
def health():
    """Simple health-check endpoint, handy while testing."""
    return jsonify({
        "status": "ok",
        "provider": "google" if GOOGLE_API_KEY else "mymemory",
    })


@app.route("/translate", methods=["POST"])
def translate():
    """
    Expected JSON body:
        { "text": "Hello", "source": "en", "target": "hi" }

    Successful response:
        { "translated_text": "..." , "source": "en", "target": "hi" }

    Error response:
        { "error": "message" }  with a 4xx / 5xx status code
    """
    try:
        data = request.get_json(silent=True) or {}

        text = (data.get("text") or "").strip()
        source = (data.get("source") or "auto").strip().lower()
        target = (data.get("target") or "").strip().lower()

        # ---- Validation -------------------------------------------------
        if not text:
            return jsonify({"error": "Please enter some text to translate."}), 400

        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                "error": f"Text is too long. Maximum {MAX_TEXT_LENGTH} characters."
            }), 400

        if source not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unsupported source language: {source}"}), 400

        if target not in SUPPORTED_LANGUAGES or target == "auto":
            return jsonify({"error": f"Unsupported target language: {target}"}), 400

        if source == target:
            return jsonify({
                "error": "Source and target languages are the same."
            }), 400

        # ---- Call the translation provider -------------------------------
        if GOOGLE_API_KEY:
            translated = _translate_with_google(text, source, target)
        else:
            translated = _translate_with_mymemory(text, source, target)

        return jsonify({
            "translated_text": translated,
            "source": source,
            "target": target,
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "The translation service timed out. Please try again."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Network error. Please check your internet connection."}), 502
    except TranslationError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception:  # noqa: BLE001 - last-resort safety net
        app.logger.exception("Unexpected server error")
        return jsonify({"error": "Unexpected server error. Please try again."}), 500


# ---------------------------------------------------------------------------
# Translation providers
# ---------------------------------------------------------------------------

class TranslationError(Exception):
    """Raised when the translation provider returns an error."""


def _translate_with_google(text: str, source: str, target: str) -> str:
    """Translate using the Google Cloud Translation API (v2)."""
    payload = {"q": text, "target": target, "format": "text"}
    if source != "auto":
        payload["source"] = source

    response = requests.post(
        GOOGLE_ENDPOINT,
        params={"key": GOOGLE_API_KEY},
        data=payload,
        timeout=15,
    )

    if response.status_code != 200:
        message = "Translation API error."
        try:
            message = response.json()["error"]["message"]
        except Exception:  # noqa: BLE001
            pass
        raise TranslationError(message)

    result = response.json()
    try:
        return html.unescape(result["data"]["translations"][0]["translatedText"])
    except (KeyError, IndexError):
        raise TranslationError("Unexpected response from the translation API.")


def _translate_with_mymemory(text: str, source: str, target: str) -> str:
    """Free fallback provider so the app works without a Google API key."""
    src = "en" if source == "auto" else source

    response = requests.get(
        MYMEMORY_ENDPOINT,
        params={"q": text, "langpair": f"{src}|{target}"},
        timeout=15,
    )

    if response.status_code != 200:
        raise TranslationError("Translation service is unavailable right now.")

    result = response.json()
    translated = (result.get("responseData") or {}).get("translatedText")

    if not translated:
        raise TranslationError("Could not translate the given text.")

    return html.unescape(translated)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
