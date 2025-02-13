import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

STABLE_DIFFUSION_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY")

async def generate_image_with_stable_diffusion(prompt: str) -> str:
    """
    Generates an image using Stable Diffusion based on the given prompt.
    
    Args:
    prompt (str): The text prompt to generate the image from.
    
    Returns:
    str: URL of the generated image.
    """
    api_host = 'https://api.stability.ai'
    api_endpoint = f"{api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {STABLE_DIFFUSION_API_KEY}"
    }
    
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_endpoint, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Non-200 response: {await response.text()}")
            
            response_data = await response.json()
            
            if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                image_base64 = response_data["artifacts"][0]["base64"]
                return f"data:image/png;base64,{image_base64}"
            else:
                raise Exception("No image was generated")

