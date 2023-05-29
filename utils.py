import json
from os import path


def save_answer_on_json_file(answer, json_file_name):
    """
    Save the answer in a JSON file.

    Args:
        answer (str): The answer to be saved.
        json_file_name (str): The name of the JSON file.
    """
    json.dump(answer, open(json_file_name, "w"))


def get_output_file_name(pptx_file_name):
    """
    Generates the output file name based on the PowerPoint file name.

    Args:
        pptx_file_name (str): The name of the PowerPoint file.

    Returns:
        str: The output file name.
    """
    output_file_name = path.splitext(pptx_file_name)[0] + ".json"
    return output_file_name
