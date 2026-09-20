/* =========================================================
   AI Language Translator - front-end logic
   Handles validation, API calls, copy and text-to-speech.
   The API key lives only on the server, never here.
   ========================================================= */

// ---- Grab the elements we need -------------------------------------------
const inputText    = document.getElementById("inputText");
const outputText   = document.getElementById("outputText");
const charCount    = document.getElementById("charCount");
const sourceLang   = document.getElementById("sourceLang");
const targetLang   = document.getElementById("targetLang");

const translateBtn = document.getElementById("translateBtn");
const clearBtn     = document.getElementById("clearBtn");
const swapBtn      = document.getElementById("swapBtn");
const copyBtn      = document.getElementById("copyBtn");
const speakBtn     = document.getElementById("speakBtn");

const btnLabel     = document.getElementById("btnLabel");
const spinner      = document.getElementById("spinner");
const errorBox     = document.getElementById("errorBox");
const copiedMsg    = document.getElementById("copiedMsg");

let translatedText = "";

// ---- Helpers --------------------------------------------------------------

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function setLoading(isLoading) {
  translateBtn.disabled = isLoading;
  spinner.hidden = !isLoading;
  btnLabel.textContent = isLoading ? "Translating..." : "Translate";
}

function setOutput(text) {
  translatedText = text || "";
  if (translatedText) {
    outputText.textContent = translatedText;
  } else {
    outputText.innerHTML = '<span class="placeholder">Your translation will appear here.</span>';
  }
  copyBtn.disabled = !translatedText;
  speakBtn.disabled = !translatedText;
}

// ---- Character counter ----------------------------------------------------
inputText.addEventListener("input", () => {
  charCount.textContent = inputText.value.length;
  if (inputText.value.trim()) hideError();
});

// ---- Clear button ---------------------------------------------------------
clearBtn.addEventListener("click", () => {
  inputText.value = "";
  charCount.textContent = "0";
  setOutput("");
  hideError();
  inputText.focus();
});

// ---- Swap languages -------------------------------------------------------
swapBtn.addEventListener("click", () => {
  // "Detect language" cannot be used as a target language
  if (sourceLang.value === "auto") {
    showError("Choose a specific source language before swapping.");
    return;
  }
  const temp = sourceLang.value;
  sourceLang.value = targetLang.value;
  targetLang.value = temp;

  // Also swap the texts so the user can keep working
  if (translatedText) {
    inputText.value = translatedText;
    charCount.textContent = inputText.value.length;
    setOutput("");
  }
  hideError();
});

// ---- Translate ------------------------------------------------------------
async function translate() {
  const text = inputText.value.trim();
  hideError();

  // 1. Validate input on the client as well
  if (!text) {
    showError("Please enter some text before translating.");
    inputText.focus();
    return;
  }
  if (sourceLang.value === targetLang.value) {
    showError("Source and target languages must be different.");
    return;
  }

  setLoading(true);
  setOutput("");

  try {
    // 2. Send the data to the Flask backend
    const response = await fetch("/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        source: sourceLang.value,
        target: targetLang.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Translation failed. Please try again.");
      return;
    }

    // 3. Show the translated text
    setOutput(data.translated_text);
  } catch (err) {
    showError("Could not reach the server. Please check your connection.");
  } finally {
    setLoading(false);
  }
}

translateBtn.addEventListener("click", translate);

// Ctrl + Enter also triggers a translation
inputText.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") translate();
});

// ---- Copy button ----------------------------------------------------------
copyBtn.addEventListener("click", async () => {
  if (!translatedText) return;
  try {
    await navigator.clipboard.writeText(translatedText);
  } catch {
    // Fallback for older browsers
    const temp = document.createElement("textarea");
    temp.value = translatedText;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand("copy");
    document.body.removeChild(temp);
  }
  copiedMsg.classList.add("show");
  setTimeout(() => copiedMsg.classList.remove("show"), 1600);
});

// ---- Text-to-Speech (browser SpeechSynthesis API) -------------------------
speakBtn.addEventListener("click", () => {
  if (!translatedText) return;

  if (!("speechSynthesis" in window)) {
    showError("Your browser does not support text-to-speech.");
    return;
  }

  // Stop anything currently being spoken
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(translatedText);
  utterance.lang = targetLang.value;   // e.g. "hi" for Hindi
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
});

// ---- Initial state --------------------------------------------------------
setOutput("");
