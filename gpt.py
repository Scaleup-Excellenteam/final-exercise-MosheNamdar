import os
import openai
import asyncio
from dotenv import load_dotenv
from time import time

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variable
KEY = os.environ.get("KEY")

# Variable to keep track of the number of API requests made
numbers_of_requests = 0

# Variable to keep the last request time
last_request_time = 0


async def generate_answer_gpt(slide):
    openai.api_key = KEY
    global numbers_of_requests, last_request_time

    current_time = time()
    time_elapsed = current_time - last_request_time

    request = "Hi, could you please summarize the following slides for me?\n" + slide
    if time_elapsed < 60 and numbers_of_requests >= 3:
        await asyncio.sleep(60 - time_elapsed)
        numbers_of_requests = 0
        last_request_time = current_time

    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=[
                                           {"role": "user", "content": request}
                                       ],
                                       )

    numbers_of_requests += 1
    last_request_time = time()

    if 'choices' in response:
        return response['choices'][0]['message']['content'].strip()
    else:
        return "Empty slide"
