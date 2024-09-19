import os
from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
from sragent import gather
from sragent import fetch

app = Flask(__name__)

OUTPUT_DIR = 'sragent_output'

# Function to list all files in the output directory
def list_output_files():
    files = os.listdir(OUTPUT_DIR)
    return files

# Route to home page where the user can run the gather function
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        project_ids = request.form['project_ids']
        project_list = project_ids.split(",")  # Split by comma for multiple IDs
        # Run gather function
        print(project_list)
        df = gather(project_list)
        output_file = os.path.join(OUTPUT_DIR, 'metadata.csv')
        df.to_csv(output_file, index=False)
        return redirect(url_for('view_files'))
    return render_template('index.html')

# Route to list all files in the output directory
@app.route('/files', methods=['GET'])
def view_files():
    files = list_output_files()
    return render_template('files.html', files=files)

# Route to view and edit a specific file (e.g., a summary file)
@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_file(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if request.method == 'POST':
        # Get the updated content from the form and save it back to the file
        updated_content = request.form['file_content']
        with open(filepath, 'w') as file:
            file.write(updated_content)
        return redirect(url_for('view_files'))

    # Read the file content for display in the editor
    with open(filepath, 'r') as file:
        content = file.read()
    
    return render_template('edit.html', filename=filename, content=content)

# Route to rerun the annotation for a specific project
@app.route('/rerun/<filename>', methods=['GET', 'POST'])
def rerun_annotation(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Load the summary file and rerun the annotation function
    with open(filepath, 'r') as file:
        summary = file.read()
    
    annotated_summary = annotate_summary(summary)  # Rerun the GPT-based annotation
    with open(filepath, 'w') as file:
        file.write(annotated_summary)
    
    return redirect(url_for('view_files'))

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    app.run(debug=True)
