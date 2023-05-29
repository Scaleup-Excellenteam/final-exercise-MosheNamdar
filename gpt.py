import os
import openai
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variable
KEY = os.environ.get("KEY")

# Variable to keep track of the number of API requests made
numbers_of_requests = 0


async def generate_answer_gpt(slides):
    """
    Generates an answer using OpenAI's GPT-3.5-turbo model.

    Args:
        slides (list): A list of slide texts.

    Returns:
        str: The generated answer.
    """
    openai.api_key = KEY
    global numbers_of_requests

    # Build the request message
    request = "Hi, could you please summarize the following slides for me?\n"
    answer = ""
    for i, slide in enumerate(slides):
        request += slide

        try:
            # Make an API call to generate a response
            response = await asyncio.to_thread(openai.ChatCompletion.create,
                                               model="gpt-3.5-turbo",
                                               messages=[
                                                   {"role": "system", "content": request},
                                               ])

            # Extract the answer from the API response
            slide_answer = response.choices[0].message.content.strip()
            answer += slide_answer

        except Exception as e:
            # Handle errors raised while processing a slide
            slide_error_message = f"Error processing slide {i + 1}: {str(e)}\n\n"
            answer += slide_error_message

        numbers_of_requests += 1
        prev_request_time = datetime.now()

        # Pause after every third request to stay within rate limits
        if i < len(slides) - 1 and numbers_of_requests % 3 == 0:
            time_left = timedelta(minutes=1) - (datetime.now() - prev_request_time)

            if time_left.total_seconds() > 0:
                await asyncio.sleep(time_left.total_seconds())

    return answer
