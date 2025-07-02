import io, time
import fitz
import numpy as np
from PIL import Image
import easyocr
from paddleocr import PaddleOCR

ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')  # Run this ONCE globally
# reader = easyocr.Reader(['en'])  # 'en' = English language

SUPPORTED_TYPES = ["referral_letter", "medical_certificate", "receipt"]

def ocr_page_with_paddleocr(pix):
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_np = np.array(image)

    result = ocr_engine.ocr(img_np) 
    lines = []
    for line in result:
        lines = lines + line['rec_texts']
    return lines
    #     print(line)
    #     box, (text, score) = line
    #     if score > 0.5:
    #         lines.append(text)
    # return " ".join(lines)

def classify_document(text: str):
    if "Referral No" in text or "Provisional Diagnosis" in text:
        return "referral_letter"
    if "MC Days" in text or "Date of MC" in text:
        return "medical_certificate"
    if "Total Amount Paid" in text:
        return "receipt"
    return None

def extract_fields(doc_type: str, text: str):
    # Placeholder parsers
    if doc_type == "receipt":
        return {
            "claimant_name": None,
            "provider_name": None,
            "signature_presence": None,
            "total_amount_paid": None,
            "total_approved_amount": None,
            "total_requested_amount": None
        }
        
    elif doc_type == "referral_letter":
        return{
            "date_of_birth": None,
            "gender": None,
            "location": None,
            "referral_no": None,
            "visit_date": None,
            "hospital": None,
            "department": None,
            "referral_type": None,
            "appointment_date_and_time": None,
            "appointment_centre_tel": None,
            "clinic": None,
            "block": None,
            "level": None,
            "allergies": None,
            "adverse_reaction": None,
            "indication_of_referral": None,
            "referral_details": None,
            "provisional_diagnosis": None
            }
        
    elif doc_type == "medical_certificate":
        return {
            "claimant_name": None,
            "claimant_address": None,
            "claimant_date_of_birth": False,
            "discharge_date_time": None,
            "icd_code": None,
            "provider_name": None,
            "submission_date_time": None,
            "date_of_mc": None,
            "mc_days": None,
        }
    return {}

# def ocr_page_with_easyocr(pix):
#     img_data = pix.tobytes("png")
#     image = Image.open(io.BytesIO(img_data)).convert("RGB")
#     img_np = np.array(image)
#     ocr_result = reader.readtext(img_np, detail=0)
#     return " ".join(ocr_result)

def process_file(pdf_bytes: bytes):
    start = time.time()
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    print(doc)
    print('Page Count:', doc.page_count)

    full_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            full_text += text + "\n"
        else:
            # OCR fallback
            pix = page.get_pixmap(dpi=300)
            # full_text += ocr_page_with_easyocr(pix) + "\n"
            full_text += ocr_page_with_paddleocr(pix) + "\n"
        
    doc_type = classify_document(full_text)

    fields = extract_fields(doc_type, full_text) if doc_type else {}
    
    elapsed = time.time() - start
    
    return doc_type, full_text, fields, elapsed
