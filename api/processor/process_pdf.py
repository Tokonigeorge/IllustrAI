
from pdf2image import convert_from_bytes
import numpy as np
import pytesseract
from typing import List
from cv2 import (cvtColor, COLOR_BGR2GRAY,kmeans, TERM_CRITERIA_EPS, TERM_CRITERIA_MAX_ITER, KMEANS_PP_CENTERS)
from api.processor.branding import send_to_gemini
from api.processor.generate_image import generate_image_with_stable_diffusion
from api.processor.branding import refine_prompt_with_gemini
from typing import Dict, Any
from api.processor.branding import encode_image
import asyncio
from collections import Counter

def generate_weighted_prompt(gemini_results: Dict[int, str], user_query: str) -> str:
    """
    Generates a weighted prompt based on recurring elements from Gemini results,
    prioritizing elements specified in the user query.
    """
    
    # Tokenize and count occurrences of words and phrases
    element_counter = Counter()
    
    for result in gemini_results.values():
        words = result.lower().split()
        element_counter.update(words)
    
    # Extract keywords from user query
    user_query_keywords = set(user_query.lower().split())
    
    # Sort elements by frequency but prioritize those in the user query
    sorted_elements = sorted(
        element_counter.items(), 
        key=lambda x: (x[0] in user_query_keywords, x[1]),
        reverse=True
    )
    
    # Construct prompt
    weighted_prompt = " ".join([word for word, _ in sorted_elements])
    print(f"Weighted prompt: {weighted_prompt}")
    
    return f"{user_query}: {weighted_prompt}".strip()



#configure gemini api
async def process_pdf_with_gemini(pdf_content: bytes, user_prompt: str) -> Dict[str, Any]:
    """
    Processes a PDF document by:
    1. Converting pages to images.
    2. Extracting text (OCR) & colors (K-means).
    3. Sending structured data to Gemini.
    4. Returning analyzed insights.
    """
    try:
        # Step 1: Extract text, colors, and images
        processed_data = await process_pdf_pages(pdf_content)
        print(len(processed_data), "processed data")
        # Encode images in parallel
        encode_tasks = [encode_image(data["image"]) for data in processed_data.values()]
        encoded_images = await asyncio.gather(*encode_tasks)
        # Add encoded images back to processed data
        for idx, (page_number, data) in enumerate(processed_data.items()):
            data["encoded_image"] = encoded_images[idx]
    

        # Process Gemini requests in batches of 5
        semaphore = asyncio.Semaphore(5) 

        async def process_page(page_number, data):
            print(f"Processing page {page_number}...")
            async with semaphore:
                return page_number, await send_to_gemini(data, user_prompt)

        gemini_tasks = [process_page(page_num, data) for page_num, data in processed_data.items()]
        gemini_results = await asyncio.gather(*gemini_tasks)
        structured_results = {page: result for page, result in gemini_results}
                # Step 3: Generate initial weighted prompt
        initial_prompt = generate_weighted_prompt(structured_results, user_prompt)

        # Step 4: Refine prompt using Gemini
        refined_prompt = await refine_prompt_with_gemini(initial_prompt, user_prompt)

        # Step 5: Generate image with Stable Diffusion
        image_url = await generate_image_with_stable_diffusion(refined_prompt)
        

        return {
                "success": True,
                "message": "PDF processed and analyzed successfully",
                "results": {
                "unified_prompt": refined_prompt,
                "generated_image_url": image_url,
                **structured_results
            },
            }
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise RuntimeError("Failed to process PDF") from e
   


async def process_pdf_pages( pdf_content: bytes) -> List[str]:
    """Converts PDF to images and extracts text from each page asynchronously"""
    # include poppler during deployment
    images = convert_from_bytes(pdf_content)
  
    extracted_data = {}
    print("Starting text and color extraction...")
    for page_number, image in enumerate(images, start=1):
        print(f"Processing page {page_number}...")
        try:
            #convert image to OpenCV format(numpy, array)
            image_cv = np.array(image)

            #convert to graycale for OCR
            gray = cvtColor(image_cv, COLOR_BGR2GRAY)

            #perform OCR using pytesseract
            extracted_text = pytesseract.image_to_string(gray)

            #extract dominant colors
            dominant_colors = extract_dominant_colors(image_cv)

            #store results
            extracted_data[page_number] = {
                'text': extracted_text,
                'colors': dominant_colors,
                'image': image
            }
            print("Text and color extraction complete")
            return extracted_data
        except Exception as e:
            print(f"Error processing page {page_number}: {e}")
            raise RuntimeError(f"Failed to process page {page_number}") from e
 


def extract_dominant_colors(image: np.ndarray, k: int = 3) -> List[str]:
    try:
        #reshape image for clustering
        pixels = image.reshape(-1, 3)
        print(f"Pixels shape: {pixels.shape}")

        #convert to float32 for kmeans
        pixels = np.float32(pixels)

        #define criteria and apply kmeans
        criteria = (TERM_CRITERIA_EPS + TERM_CRITERIA_MAX_ITER, 10, 0.1)
        print(f"Running KMeans with k={k}")
        _, labels, centroids = kmeans(pixels, k, None, criteria, 10,KMEANS_PP_CENTERS)
        
        #convert centroids to hex color code
        colors = [f"#{int(c[0]):02X}{int(c[1]):02X}{int(c[2]):02X}" for c in centroids]
        print(f"Extracted {len(colors)} dominant colors")
        return colors
    except Exception as e:
        print(f"Error extracting dominant colors: {e}")
        raise RuntimeError("Failed to extract dominant colors") from e
        
