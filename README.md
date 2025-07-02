# OCR-Endpoint
OCR Endpoint

Setup:

Install dependencies (pip install -r requirements.txt)

Install Tesseract/Wkhtmltopdf/poppler for pdf2image

Run:

uvicorn app.main:app --reload

Usage:

curl -F file=@receipt.pdf http://localhost:8000/ocr

Extensibility:

Add new classify_document rules

Extend extract_fields logic per document type

Override OCR engine if switching from Tesseract