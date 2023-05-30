import asyncio
from os import path
from pptx_parser import read_presentation
from gpt import generate_answer_gpt
from utils import save_answer_on_json_file, get_output_file_name


async def main():
    """
    Main function to execute the program.
    """
    path_of_pptx = input("please enter a path: ")

    presentation_text = read_presentation(path_of_pptx)

    answer = await generate_answer_gpt(presentation_text)
    # print(answer)

    json_file_name = get_output_file_name(path.basename(path_of_pptx))

    save_answer_on_json_file(answer, json_file_name)


if __name__ == '__main__':
    asyncio.run(main())
