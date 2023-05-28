import os
from pptx import Presentation
import openai
import asyncio
import collections.abc
import json
from os import path
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
KEY = os.environ.get("KEY")

numbers_of_requests = 0


def save_answer_on_json_file(answer, jason_file_name):
    json.dump(answer, open(jason_file_name, "w"))


async def generate_answer_gpt(slides):
    openai.api_key = KEY
    global numbers_of_requests

    request = "Hi,could you please summarize the following slides for me?\n"
    for i, slide in enumerate(slides):
        request += slide
        response = await asyncio.to_thread(openai.ChatCompletion.create,
                                           model="gpt-3.5-turbo",
                                           messages=[
                                               {"role": "system", "content": request},
                                           ],
                                           max_tokens=1000)

        answer = response.choices[0].message.content.strip()
        answer = answer.replace(". ", ".\n")
        numbers_of_requests += 1
        prev_request_time = datetime.now()

        if i < len(slides) - 1 and numbers_of_requests % 3 == 0:
            time_left = timedelta(minutes=1) - (datetime.now() - prev_request_time)

            if time_left.total_seconds() > 0:
                await asyncio.sleep(time_left.total_seconds())

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
