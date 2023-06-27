import asyncio
import os
from datetime import datetime
from db import session, Upload
from pptx_parser import read_presentation
from gpt import generate_answer_gpt
from utils import save_answer_on_json_file


async def main():
    """
    Main function to execute the program.

    This function continuously scans the uploads folder for pending files.
    It processes each pending file by generating answers using GPT for each slide in the presentation.
    The answers are then saved in a JSON file and the status of the file is updated to 'done'.
    The processed files are deleted from the uploads folder.
    """
    while True:
        asyncio.sleep(10)
        # Scan the uploads folder
        pending = session.query(Upload).filter(Upload.status == "pending").all()

        for file in pending:
            uid = file.uid
            path_of_pptx = "uploads\\" + uid + ".pptx"
            presentation_text = read_presentation(path_of_pptx)
            upload_time = datetime.now()
            update_status(uid, "pending", upload_time=upload_time)
            answer = []
            for slide in presentation_text:
                generate_text = await generate_answer_gpt(slide)
                answer.append(generate_text)
            joined_answers = ' '.join(answer)
            json_file_name = uid + ".json"

            save_answer_on_json_file(joined_answers, json_file_name)

            finish_time = datetime.now()
            update_status(uid, "done", finish_time=finish_time)
            file_to_delete = uid + ".pptx"
            delete_file(file_to_delete)


def update_status(uid, status, upload_time=None, finish_time=None):
    """
    Update the status of the file with the given UID in the database.

    Parameters:
    - uid (str): The UID of the file.
    - status (str): The new status to be set.
    - upload_time (datetime): The upload time (optional).
    - finish_time (datetime): The finish time (optional).

    Returns:
    - None.
    """
    upload = session.query(Upload).filter_by(uid=uid).first()
    if upload:
        upload.status = status
        if upload_time:
            upload.upload_time = upload_time
        if finish_time:
            upload.finish_time = finish_time
        session.commit()
    else:
        print(f"No record found in the database with UID '{uid}'.")


def delete_file(file_to_delete):
    """
    Delete the file with the given name from the uploads folder.

    Parameters:
    - file_to_delete (str): The name of the file to be deleted.

    Raises:
    - FileNotFoundError: If the file is not found in the uploads folder.

    Returns:
    - None.
    """
    uploads_folder = "uploads"

    file_path = os.path.join(uploads_folder, file_to_delete)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_to_delete}' was not found in the uploads folder.")

    os.remove(file_path)


if __name__ == '__main__':
    asyncio.run(main())
