import asyncio
import os
import shutil
from os import path
from pptx_parser import read_presentation
from gpt import generate_answer_gpt
from utils import save_answer_on_json_file, get_output_file_name


async def main():
    """
    Main function to execute the program.
    """
    while True:
        asyncio.sleep(10)
        # Scan the uploads folder
        files = os.listdir('uploads')

        for file in files:
            path_of_pptx = os.path.join('uploads', file)

            presentation_text = read_presentation(path_of_pptx)

            status_management(path_of_pptx, True)

            answer = await generate_answer_gpt(presentation_text)
            # print(answer)
            path_of_json = os.path.join('outputs', file)
            json_file_name = get_output_file_name(path.basename(path_of_json))

            save_answer_on_json_file(answer, json_file_name)

            status_management(path_of_pptx, False)


def status_management(file_path, flag):
    file_name = os.path.basename(file_path)
    pending_folder = 'pending'

    if flag:
        if not os.path.exists(pending_folder):
            os.makedirs(pending_folder)

        shutil.move(file_path, os.path.join(pending_folder, file_name))
    else:
        file_in_pending = os.path.join(pending_folder, file_name)
        if os.path.exists(file_in_pending):
            os.remove(file_in_pending)


if __name__ == '__main__':
    asyncio.run(main())
