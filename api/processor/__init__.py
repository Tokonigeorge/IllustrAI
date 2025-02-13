from api.processor.process_pdf import process_pdf_with_gemini
from typing import List

class PDFProcessingService:
    @staticmethod
    async def process_document(pdf_content: bytes, user_prompt: str) -> dict:
        """
        Service method to handle PDF processing
        Returns a dictionary with the processing results
        """
        try:
            print("pdf processing service...")
            extracted_data = await process_pdf_with_gemini(pdf_content, user_prompt)
            return {
                "success": True,
                "message": "PDF content processed successfully",
                "results": extracted_data["results"]
            }
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}",
                "results": None
            }
        
__all__ = ["PDFProcessingService"]