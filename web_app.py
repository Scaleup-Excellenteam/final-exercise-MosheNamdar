import logging
from flask import Flask, request, render_template, redirect, url_for
import os
import uuid
from sqlalchemy import desc
from db import session, User, Upload

app = Flask(__name__)

UPLOAD = 'uploads'
PENDING = 'pending'
DONE = 'outputs'

app.config['UPLOAD'] = UPLOAD

if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD)

if not os.path.exists(DONE):
    os.makedirs(DONE)


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
            file.save(os.path.join(app.config['UPLOAD'], filename))
            uid = filename.split('.')[0]
            user_email = request.form.get('email')
            original_file_name = os.path.basename(file.filename)
            save_on_db(uid, user_email, original_file_name)

            return render_template('upload_page.html', message='File uploaded successfully!', uid=uid)

    return render_template('upload_page.html')


def save_on_db(uid, user_email, filename):
    if user_email:
        # Check if the email already exists in the Users table
        existing_user = session.query(User).filter_by(email=user_email).first()
        if existing_user:
            # User already exists, create an Upload associated with the user
            upload = Upload(uid=uid, filename=filename, status=get_status(uid), user_id=existing_user.id)
            upload.set_finish_time()
        else:
            # User doesn't exist, create a new User and an associated Upload
            new_user = User(email=user_email)
            session.add(new_user)
            session.commit()
            # Retrieve the newly created user from the session
            new_user = session.query(User).filter_by(email=user_email).first()
            upload = Upload(uid=uid, filename=filename, status=get_status(uid), user_id=new_user.id)
            upload.set_finish_time()

        session.add(upload)
        session.commit()

    else:
        # User did not provide an email, create Upload without User
        upload = Upload(uid=uid, filename=filename, status=get_status(uid))
        upload.set_finish_time()
        session.add(upload)
        session.commit()


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
    uid = str(uuid.uuid4().hex)
    filename_without_extension, extension = os.path.splitext(file_name)
    new_filename = f"{uid}{extension}"
    return new_filename


def get_status(file_name):
    try:
        upload = session.query(Upload).filter_by(uid=file_name).first()
        if upload:
            return upload.status
        else:
            return 'pending'
    except Exception as e:
        print("Error: Failed to retrieve the file status. Reason: %s", str(e))
        return 'not found'


def get_details(file_name):
    try:
        upload = get_upload(file_name)

        return {
            'status': upload.status if upload else None,
            'filename': upload.filename.split('_', 1)[0] if upload else None,
            'timestamp': upload.upload_time if upload else None,
            'explanation': get_explanation(file_name) if upload else None
        }
    except Exception as e:
        # Handle any exceptions that may occur during the file details retrieval
        print(f"An error occurred while retrieving file details: {str(e)}")
        return {}


def get_upload(file_name):
    upload = session.query(Upload).filter_by(uid=file_name).first()
    return upload


def get_explanation(file_name):
    try:
        explanation_file_path = os.path.join(DONE, file_name) + '.json'
        if os.path.exists(explanation_file_path):
            with open(explanation_file_path, "r") as explanation_file:
                explanation_text = explanation_file.read()
            return explanation_text
        else:
            return "pending... try to refresh"
    except Exception as ex:
        # Handle any exceptions that may occur during the explanation retrieval
        print(f"An error occurred while retrieving the file explanation: {str(ex)}")
        return "An error occurred while retrieving the file explanation. Please try again later."


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
        email = request.form.get('email')
        filename = request.form.get('filename')
        if uid:
            try:
                file_details = get_details(uid)
                return render_template('status.html', data=file_details)
            except Exception as e:
                print(f"An error occurred while retrieving file status: {str(e)}")
                return redirect(url_for('index', error='An error occurred while retrieving file status'))
        elif email and filename:
            try:
                uid = get_uid(email, filename)
                file_details = get_details(uid)
                return render_template('status.html', data=file_details)
            except Exception as e:
                print(f"An error occurred while retrieving file status: {str(e)}")
                return redirect(url_for('index', error='An error occurred while retrieving file status'))
        else:
            return redirect(url_for('index', error='UID or Email & Filename not provided'))
    else:
        return render_template('index.html')


class UIDNotFoundException(Exception):
    pass


def get_uid(email, filename):
    try:
        user = session.query(User).filter_by(email=email).first()
        if user:
            last_upload = session.query(Upload).filter_by(filename=filename, user=user).order_by(
                desc(Upload.upload_time)).first()

            if last_upload:
                return last_upload.uid

        raise UIDNotFoundException("No matching record found for the given email and filename")
    except Exception as e:
        logging.error(f"An error occurred while retrieving UID: {str(e)}")
        raise UIDNotFoundException("An error occurred while retrieving UID")


if __name__ == '__main__':
    app.run()
