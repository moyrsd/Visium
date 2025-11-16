from fastapi import APIRouter, HTTPException, UploadFile
import pymupdf

router = APIRouter()
def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        pdf_content = pdf_file.file.read()
        pdf_document = pymupdf.open(stream=pdf_content, filetype="pdf")
        extracted_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            extracted_text += page.get_text()
        pdf_document.close()
        pdf_file.file.seek(0)
        
        if not extracted_text.strip():
            raise HTTPException(400, "No text could be extracted from the PDF")
        
        return extracted_text.strip()
    
    except Exception as e:
        raise HTTPException(400, f"Error processing PDF: {str(e)}")
