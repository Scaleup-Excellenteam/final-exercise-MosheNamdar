from flask import Flask, request, render_template
import os
from datetime import datetime
import uuid
import json
import re


app = Flask(__name__)


UPLOAD = 'uploads'
PENDING = 'pending'
DONE = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD

if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the main page for file upload and processes the uploaded file.

    Method:
    - GET and POST

    Returns:
    - GET: Renders the 'upload_page.html' template.
    - POST: Uploads the file, generates a custom filename, saves the file,
            extracts information from the filename, and renders the 'upload_page.html' template
            with the extracted information.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'File not uploaded'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        if file and is_valid_file(file.filename):
            filename = generate_custom_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            regex = r'(.+?)_\d{14}_(\w+)\.pptx'
            match = re.search(regex, filename)
            # print(match)
            extracted_string = match.group(2)
            # print(extracted_string)

            return render_template('upload_page.html', message='File uploaded successfully.', uid=extracted_string)

    return render_template('upload_page.html')


def is_valid_file(filename):
    """
    Checks if the given filename has a valid extension.

    Parameters:
    - filename (str): The name of the file.

    Returns:
    - True if the file has a valid extension.
    - False otherwise.
    """
    valid_extensions = {'pptx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in valid_extensions


def generate_custom_filename(file_name):
    """
    Generates a custom filename by appending a timestamp and a unique ID to the original filename.

    Parameters:
    - file_name (str): The original filename.

    Returns:
    - The custom filename (str).
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    uid = str(uuid.uuid4().hex)
    filename_without_extension, extension = os.path.splitext(file_name)
    new_filename = f"{filename_without_extension}_{timestamp}_{uid}{extension}"
    return new_filename


def get_status(file_name):
    """
    Gets the status of a file based on its name.

    Parameters:
    - file_name (str): The name of the file.

    Returns:
    - 'done' if the file exists in the 'outputs' folder as either a .pptx or .json file.
    - 'pending' if the file exists in the 'pending' folder.
    - 'not found' if the file does not exist.
    """
    pptx_filepath = os.path.join(DONE, os.path.splitext(file_name)[0] + '.pptx')
    json_filepath = os.path.join(DONE, os.path.splitext(file_name)[0] + '.json')

    if os.path.isfile(pptx_filepath):
        return 'done'
    elif os.path.isfile(json_filepath):
        return 'done'
    elif os.path.isfile(os.path.join(PENDING, file_name)):
        return 'pending'
    else:
        return 'not found'


def get_details(file_name):
    """
    Retrieves details about a file, including the status, original filename, timestamp, and explanation.

    Parameters:
    - file_name (str): The name of the file.

    Returns:
    - A dictionary containing the file details:
        - 'status': The status of the file (str).
        - 'filename': The original filename (str).
        - 'timestamp': The formatted timestamp (str).
        - 'explanation': The explanation data (dict) or None.
    """
    filename_without_extension, _ = os.path.splitext(file_name)
    timestamp, uid = filename_without_extension.rsplit('_', 2)[-2:]
    original_filename = filename_without_extension.split('_', 1)[0]

    date_and_time = format_timestamp(timestamp)
    the_status = get_status(file_name)
    explanation = get_explanation(file_name)

    return {'status': the_status, 'filename': original_filename, 'timestamp': date_and_time, 'explanation': explanation}


def get_explanation(file_name):
    """
    Retrieves the explanation data from a .json file corresponding to the given file name.

    Parameters:
    - file_name (str): The name of the file.

    Returns:
    - The explanation data (dict) if the .json file exists and can be loaded successfully.
    - None otherwise.
    """
    output_file_path = os.path.join(DONE, os.path.splitext(file_name)[0] + '.json')

    try:
        with open(output_file_path, 'r') as file:
            explanation_data = json.load(file)
            return explanation_data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


@app.route('/status', methods=['GET', 'POST'])
def status():
    """
    Renders the status page and processes the file details based on the HTTP request method.

    Method:
    - GET and POST

    Returns:
    - GET: Renders the 'status.html' template with the file details.
    - POST: Retrieves the UID from the form data, finds the corresponding file name,
             retrieves the file details, and renders the 'status.html' template with the file details.
    """
    if request.method == 'POST':
        uid = request.form.get('uid')
        file_name = find_file_name(uid)
        details = get_details(file_name)
        return render_template('status.html', data=details)

    file_name = request.args.get('filename')
    if file_name:
        details = get_details(file_name)
        return render_template('status.html', data=details)


def find_file_name(uid):
    """
    Finds the file name that contains the given UID in its name.

    Parameters:
    - uid (str): The UID to search for.

    Returns:
    - The file name (str) if a matching file is found.
    - None otherwise.
    """
    folders = ['uploads', 'pending', 'outputs']
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file_name in files:
                if uid in file_name:
                    return os.path.basename(file_name)


def format_timestamp(timestamp):
    """
    Formats the timestamp string into a specific format.

    Parameters:
    - timestamp (str): The timestamp to format.

    Returns:
    - The formatted timestamp (str) in the format: "YYYY-MM-DD at HH:MM:SS" if successful.
    - None if an IndexError or TypeError occurs during formatting.
    """
    try:
        formatted_timestamp = "{}-{}-{} at {}:{}:{}".format(
            timestamp[:4], timestamp[4:6], timestamp[6:8],
            timestamp[8:10], timestamp[10:12], timestamp[12:14]
        )
        return formatted_timestamp
    except (IndexError, TypeError):
        return None


if __name__ == '__main__':
    app.run()
