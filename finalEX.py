from pptx import Presentation
import openai
import asyncio
import collections.abc
import json
from os import path

#KEY =


def save_answer_on_json_file(answer, jason_file_name):
    json.dump(answer, open(jason_file_name, "w"))


async def generate_answer_gpt(slides):
    openai.api_key = KEY

    request = "Hi,could you please summarize the following slides for me?\n"
    for slide in slides:
        request += slide

    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=[
                                           {"role": "system", "content": request},
                                       ],
                                       max_tokens=1000)

    answer = response.choices[0].message.content.strip()
    answer = answer.replace(". ", ".\n")

    return answer


def read_presentation(pptx_path):
    file = Presentation(pptx_path)
    text = []
    for slide in file.slides:
        text_slide = ""
        for shape in slide.shapes:
            if shape.has_text_frame:
                for ph in shape.text_frame.paragraphs:
                    text_slide += ph.text
        text.append(text_slide)

    print(text)
    return text


async def main():
    path_of_pptx = input("please enter a path: ")
    presentation_text = read_presentation(path_of_pptx)
    answer = await generate_answer_gpt(presentation_text)
    print(answer)

    jason_file_name = path.splitext(path_of_pptx)[0] + ".json"
    save_answer_on_json_file(answer, jason_file_name)


if __name__ == '__main__':
    asyncio.run(main())
