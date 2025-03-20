from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import pandas as pd

app = Flask(__name__)

# Define folders
UPLOAD_FOLDER = 'uploads'
CLEANED_FOLDER = 'cleaned'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLEANED_FOLDER'] = CLEANED_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# Allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render the form
@app.route('/')
def index():
    return render_template('index.html')  # Ensure 'index.html' is in the templates folder

# Handle file upload and cleaning
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('csvFile')
    model = request.form.get('model')  # Get the selected model

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Read and clean the CSV file
        cleaned_data = clean_csv(file_path, model)

        # Save the cleaned data
        cleaned_filename = f"cleaned_{filename}"
        cleaned_path = os.path.join(app.config['CLEANED_FOLDER'], cleaned_filename)
        cleaned_data.to_csv(cleaned_path, index=False)  # Save cleaned CSV

        # Redirect to the result page with model and filename
        return redirect(url_for('show_result', model=model, filename=cleaned_filename))
    
    return 'File not allowed or no model selected', 400

# Route to display result with selected algorithm
@app.route('/result')
def show_result():
    model = request.args.get('model')
    filename = request.args.get('filename')

    return render_template('result.html', model=model, filename=filename)

# Function to clean the CSV file based on selected model
def clean_csv(file_path, model):
    df = pd.read_csv(file_path)

    if model == "basic":
        df = basic_clean(df)
    elif model == "advanced":
        df = advanced_clean(df)
    else:
        df = df  # No cleaning applied if no model is selected

    return df

# Basic cleaning model
def basic_clean(df):
    # Example: Remove rows with any null values
    df = df.dropna()
    return df

# Advanced cleaning model (you can add more complex logic)
def advanced_clean(df):
    # Example: Convert all text to uppercase
    df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
    return df

# Function to serve the cleaned file for download
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CLEANED_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
