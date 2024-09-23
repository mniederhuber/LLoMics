from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from sragent import gather

app = Flask(__name__)

# Directory where the output files are stored
OUTPUT_DIR = 'sragent_output'

@app.route('/')
def index():
    # Render the single-page layout
    return render_template('index.html')

@app.route('/files')
def list_files():
    # List all files in the output directory
    files = os.listdir(OUTPUT_DIR)
    return jsonify(files)

@app.route('/file/<filename>')
def get_file(filename):
    # Read the content of a file and send it to the client
    with open(os.path.join(OUTPUT_DIR, filename), 'r') as f:
        content = f.read()
    return jsonify(content=content)

@app.route('/file/edit/<filename>', methods=['POST'])
def edit_file(filename):
    # Save the modified content to the file
    new_content = request.json['content']
    with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
        f.write(new_content)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
