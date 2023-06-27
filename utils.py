import json
import os
from os import path


def save_answer_on_json_file(answer, json_file_name):
    output_folder = os.path.abspath('outputs')
    os.makedirs(output_folder, exist_ok=True)
    file_path = path.join(output_folder, path.basename(json_file_name))
    with open(file_path, "w") as f:
        json.dump(answer, f)


