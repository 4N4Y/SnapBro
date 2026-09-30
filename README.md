# StudySnap

> An AI-powered study companion designed to help students learn from their own study material, with a modular path toward Snapdragon on-device AI.

## Overview

StudySnap lets students upload study material such as PDFs and ask questions about the content.

**Upload document → Extract text → Choose inference path → Ask a question → Get an answer**

The project now exposes one application-facing inference contract with two providers:

```text
                          ┌── GeminiProvider ───────────────► Gemini API
Application → ai_layer.py ┤
                          └── SnapdragonProvider (mock) ───► future Qualcomm runtime → Hexagon NPU
```

The provider is selected per request from the UI (`cloud` or `local`). The server keeps the Gemini API key on the server and never sends it to the browser.

## Current features

- PDF/TXT upload and text extraction with PyMuPDF
- Question answering against the uploaded document
- Cloud inference through the existing Gemini API integration
- A provider-neutral `InferenceProvider` abstraction
- A transparent Snapdragon local-provider placeholder for development
- Environment-variable configuration for credentials and the default provider

## Inference architecture

### Cloud AI path (available when `GEMINI_API_KEY` is configured)

```text
Application → InferenceProvider → GeminiProvider → google-genai → Gemini API
```

The existing Gemini model fallback behavior remains in `GeminiProvider` in [`ai_layer.py`](ai_layer.py).

### Snapdragon path (architecture ready; hardware execution not included)

```text
Application → InferenceProvider → SnapdragonProvider
                                      │
                                      └─ future Qualcomm AI Runtime / QNN / AI Engine Direct
                                             │
                                             └─ Hexagon NPU (where supported)
```

At present, `SnapdragonProvider` returns a deterministic mock response. It does **not** claim to detect or use Snapdragon hardware, Qualcomm AI Runtime, QNN, AI Engine Direct, or a compiled model. This is intentional because this repository does not include compatible hardware bindings or a Qualcomm-optimized model artifact.

The future implementation boundary is commented in `SnapdragonProvider.infer()`:

1. Load a Qualcomm AI Hub-optimized ONNX or equivalent compiled model.
2. Create a Qualcomm AI Runtime/QNN (AI Engine Direct) session.
3. Bind tokenizer and tensor inputs.
4. Execute on the Hexagon NPU where the target device/runtime supports it.
5. Convert the model output into the same `InferenceResult` returned by the abstraction.

This keeps Qualcomm-specific dependencies out of the base application until a target Snapdragon device, SDK/runtime version, model format, and deployment process are selected.

## Configuration

Create a local `.env` file (never commit it):

```env
GEMINI_API_KEY=your_real_key_here
# Optional: cloud (default) or local
AI_PROVIDER=cloud
```

The browser can override the default provider per question through the inference-path selector. No API key is accepted from the browser.

## Technology stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Cloud AI:** Gemini via `google-genai`
- **Local AI seam:** Python provider interface with a mock Snapdragon implementation
- **PDF processing:** PyMuPDF
- **Configuration:** `python-dotenv`

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

To run the provider tests without network access:

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
app.py                    Flask routes and document lifecycle
ai_layer.py               Provider interface, Gemini provider, Snapdragon mock
static/script.js          Upload, provider selection, and question UI
templates/index.html      Existing UI plus inference-path selector
tests/test_ai_layer.py    Offline provider contract tests
```

## Planned features

- AI-generated quizzes
- Weak-topic detection
- Knowledge maps
- Adaptive “Teach Me” mode
- Voice-based interaction
- Image/problem understanding
- Qualcomm AI Hub model optimization and Snapdragon device deployment
