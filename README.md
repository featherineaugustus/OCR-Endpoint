# OCR-Endpoint
OCR Endpoint


# Install dependencies
```bash
pip3 install -r requirements.txt
```

# Run uvicorn server
```bash
uvicorn app.main:app --reload
```

# Run medical certificate
```bash
curl -F file=@'OCR-Endpoint\Documents\Assessment_Documents\medical_certificate.pdf' \
    http://127.0.0.1:8000/ocr
```

# Run receipt
```bash
curl -F file=@'OCR-Endpoint\Documents\Assessment_Documents\receipt.pdf' \
    http://127.0.0.1:8000/ocr
```

# Run referral letter
```bash
curl -F file=@'OCR-Endpoint\Documents\Assessment_Documents\referral_letter.pdf' \
    http://127.0.0.1:8000/ocr
```

Extensibility:
- Add new classify_document rules
- Extend extract_fields logic per document type
- Override OCR engine if switching from Tesseract