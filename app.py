import os
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Configure uploads folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    """Renders the StudySnap homepage."""
    return render_template('index.html')


if __name__ == '__main__':
    # Run server on http://127.0.0.1:5000
    # use_reloader=False prevents background restarts on Windows/OneDrive
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
