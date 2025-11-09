import PyPDF2
import io

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
