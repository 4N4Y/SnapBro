import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pymupdf  # PyMuPDF for document text extraction
from dotenv import load_dotenv

from ai_layer import (
    InferenceRequest,
    InvalidCredentialsError,
    ProviderError,
    RetryableProviderError,
    get_provider,
)

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure uploads folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size

# Allowed document formats
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory document storage holding extracted text for the next step (AI model integration)
CURRENT_DOCUMENT = {
    "filename": None,
    "filepath": None,
    "text": None,
    "char_count": 0,
    "word_count": 0,
    "page_count": 0,
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    """Renders the StudySnap homepage."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle a document upload, extract text with PyMuPDF, and store it in memory."""
    file = request.files.get('document') or request.files.get('file')
    if not file or file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected. Please select a PDF document to upload."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": "Unsupported file format. Please upload a PDF document (.pdf)."
        }), 400

    try:
        filename = secure_filename(file.filename) or "uploaded_document.pdf"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.lower().endswith('.pdf'):
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            pages_text = [doc[page_idx].get_text() for page_idx in range(page_count)]
            doc.close()
            extracted_text = "\n".join(pages_text).strip()
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                extracted_text = f.read().strip()
            page_count = 1

        char_count = len(extracted_text)
        word_count = len(extracted_text.split())
        CURRENT_DOCUMENT.update({
            "filename": filename,
            "filepath": file_path,
            "text": extracted_text,
            "char_count": char_count,
            "word_count": word_count,
            "page_count": page_count,
        })

        text_cache_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.extracted.txt")
        with open(text_cache_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        preview_snippet = extracted_text[:300].strip()
        if len(extracted_text) > 300:
            preview_snippet += "..."

        return jsonify({
            "success": True,
            "filename": filename,
            "characters": char_count,
            "words": word_count,
            "pages": page_count,
            "preview": preview_snippet,
            "message": f"Successfully extracted {word_count:,} words ({char_count:,} characters) across {page_count} page(s)."
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to extract text from PDF: {str(e)}"
        }), 500


@app.route('/api/document', methods=['GET'])
def get_current_document():
    """Return the currently stored document metadata and extracted text."""
    if not CURRENT_DOCUMENT.get("text"):
        return jsonify({
            "has_document": False,
            "message": "No document has been extracted yet."
        }), 404

    return jsonify({
        "has_document": True,
        "filename": CURRENT_DOCUMENT["filename"],
        "characters": CURRENT_DOCUMENT["char_count"],
        "words": CURRENT_DOCUMENT["word_count"],
        "pages": CURRENT_DOCUMENT["page_count"],
        "text": CURRENT_DOCUMENT["text"]
    }), 200


@app.route('/api/ask', methods=['POST'])
@app.route('/ask', methods=['POST'])
def ask_question():
    """Answer a question through the requested cloud or local inference provider."""
    document_text = CURRENT_DOCUMENT.get("text")
    if not document_text:
        return jsonify({
            "success": False,
            "error": "No document has been uploaded yet. Upload a PDF first, then ask a question."
        }), 400

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or request.form.get("question") or "").strip()
    if not question:
        return jsonify({
            "success": False,
            "error": "Please enter a question about the uploaded study material."
        }), 400

    requested_provider = payload.get("provider") or request.form.get("provider")
    try:
        provider = get_provider(requested_provider)
        result = provider.infer(InferenceRequest(
            question=question,
            document_text=document_text,
            filename=CURRENT_DOCUMENT.get("filename"),
        ))
        return jsonify({
            "success": True,
            "answer": result.answer,
            "provider": result.provider,
            "model": result.model,
            "execution": result.metadata.get("execution"),
            "filename": CURRENT_DOCUMENT.get("filename"),
        }), 200

    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except InvalidCredentialsError as exc:
        return jsonify({"success": False, "error": str(exc)}), 503
    except RetryableProviderError:
        return jsonify({
            "success": False,
            "error": "Gemini is busy or the requested model is unavailable. Wait a few seconds and ask again."
        }), 503
    except ProviderError:
        return jsonify({
            "success": False,
            "error": "The selected AI provider request failed. Please try again in a moment."
        }), 502


if __name__ == '__main__':
    # Run server on http://127.0.0.1:5000
    # use_reloader=False prevents background restarts on Windows/OneDrive
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
