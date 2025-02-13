import os
from dotenv import load_dotenv
from google.generativeai import GenerativeModel
import google.generativeai as genai
import asyncio
from io import BytesIO
from PIL import Image
import base64
from typing import Dict, Any
import logging


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY not found in environment variables.")
    raise ValueError("GOOGLE_API_KEY not found in environment variables.  Make sure you have created the .env file and it has the correct API KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

async def encode_image(image: Image.Image) -> str:
    """
    Converts a PIL image to a base64-encoded string asynchronously.
    """
    try:
        logging.info(f"Starting image encoding process for image size: {image.size}")

        buffer = BytesIO()
        image.save(buffer, format="JPEG")  # Ensure correct format
        encoded = await asyncio.to_thread(
            lambda: base64.b64encode(buffer.getvalue()).decode('utf-8')
        )

        logging.info("Successfully encoded image to base64")
        return encoded
    
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        raise ValueError(f"Failed to encode image: {str(e)}")
    
async def send_to_gemini(page_data: Dict[str, Any], user_prompt: str) -> str:
    """Sends text, colors, and encoded image to Gemini asynchronously and returns structured insights."""
    try:
        text = page_data["text"][:1000]  # Limit text length
        colors = ", ".join(page_data["colors"][:5])  # Limit colors
        image_base64 = page_data["encoded_image"]

        prompt = f"""
        Analyze this document page as a brand illustrator looking to create illustrations about the query following the brand style presented in the document:
        Text: {text}
        Colors: {colors}
        Query: "{user_prompt}"
        Provide:
        1. Key branding elements
        2. Theme and purpose
        3. Query-relevant insights
        """

        parts = [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}},
        ]

        logging.debug(f"Sending request to Gemini with image size: {len(image_base64)} bytes")
        response = await model.generate_content_async(parts)

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text
    except Exception as e:
        logging.error(f"Error processing Gemini request: {e}")
        raise RuntimeError(f"Gemini request failed: {e}")
    

async def refine_prompt_with_gemini(initial_prompt: str, user_query: str) -> str:
    prompt = f"""
    As an AI expert in creating prompts for illustration generation, refine and structure the following prompt:

    Initial Prompt: {initial_prompt}
    User Query: {user_query}

    Create a seamless, structured prompt for generating an illustration that:
    1. Incorporates key elements from the initial prompt
    2. Addresses the user's query
    3. Provides clear guidance for visual elements, style, and composition
    4. Is optimized for use with Stable Diffusion

    Return only the refined prompt, without any additional explanation.
    """
    try:
        response = await model.generate_content_async([{"text": prompt}])
        print(f"Refined prompt: {response.text}")
        return response.text if response.text else initial_prompt
    except Exception as e:
        logging.error(f"Error refining prompt: {e}")
        raise RuntimeError(f"Prompt refinement failed: {e}")



