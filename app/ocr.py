import io, time
import fitz
import numpy as np
from PIL import Image
import easyocr
from paddleocr import PaddleOCR

SUPPORTED_TYPES = ["referral_letter", "medical_certificate", "receipt"]

##################################################################################
# Load OCR Engine
##################################################################################
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')  # Run this ONCE globally


##################################################################################
# Perform OCR on page
##################################################################################
def ocr_page_with_paddleocr(pix):
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_np = np.array(image)

    result = ocr_engine.ocr(img_np) 
    lines = []
    for line in result:
        lines = lines + line['rec_texts']
    return lines


##################################################################################
# Classify documents
##################################################################################
def classify_document(text: str):
    text = [x.lower() for x in text]
    substring_list_referral = ['kind regards']
    substring_list_mc = ['typeofmedicalcertificate']
    substring_list_receipt = ['tax invoice']
    
    if any(x in text for x in substring_list_referral):
        return "referral_letter"
    elif any(x in text for x in substring_list_mc):
        return "medical_certificate"
    elif any(x in text for x in substring_list_receipt):
        return "receipt"
    else:
        return None


##################################################################################
# Check if a string can be converted into float
##################################################################################
def can_convert_to_float(s):
    try:
        float(s)
        return True
    except:
        return False


##################################################################################
# Extract fields - MC
##################################################################################
def extract_fields_mc(text):
    output = {
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
    
    text = [x.lower() for x in text]
    for i, item in enumerate(text):
        if 'name:' in item:
            item = item.replace('name:', '').strip()
            output['claimant_name'] = item
        elif item.endswith('days'):
            output['mc_days'] = item  
        elif item.beginsswith('from'):
            output['date_of_mc'] = item  
            
    return output


##################################################################################
# Extract fields - Receipt
##################################################################################
def extract_fields_receipt(text):
    output = {
            "claimant_name": None,
            "provider_name": None,
            "signature_presence": None,
            "total_amount_paid": None,
            "total_approved_amount": None,
            "total_requested_amount": None
        }

    text = [x.lower() for x in text]
    for i, item in enumerate(text):
        if 'self' in item:
            output['claimant_name'] = text[i+1]
        elif 'total amount paid' in item:
            i = i + 1
            while True:
                if can_convert_to_float(text[i]):
                    output['total_amount_paid'] = text[i]
                    break
                else:
                    i = i + 1
        
    return output


##################################################################################
# Extract fields - Referral
##################################################################################
def extract_fields_referral(text):
    output =             {
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
    
    text = [x.lower() for x in text]
    for i, item in enumerate(text):
        if 'id:' in item:
            output['referral_no'] = text[i]
        if '2025:' in item:
            output['appointment_date_and_time'] = text[i]
        if 'thank' in item:
            end = i + 1
            while 'kind regards' not in text[end]:
                end = end + 1
            output['referral_details'] = ' '.join(text[i:end])
            
    return output


##################################################################################
# Extract fields
##################################################################################
def extract_fields(doc_type: str, text: str):
    # Placeholder parsers
    if doc_type == "receipt":
        return extract_fields_receipt(text)
    elif doc_type == "referral_letter":
        return extract_fields_referral(text)
    elif doc_type == "medical_certificate":
        return extract_fields_mc(text)
    else:
        return {}


##################################################################################
# Process file
##################################################################################
def process_file(pdf_bytes: bytes):
    start = time.time()
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    lines = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            full_text += text + "\n"
        else:
            pix = page.get_pixmap(dpi=300)
            line =  ocr_page_with_paddleocr(pix)
            lines = lines +line['rec_texts']
        
    doc_type = classify_document(lines)
    fields = extract_fields(doc_type, lines) if doc_type else {}
    
    elapsed = time.time() - start
    
    return doc_type, full_text, fields, elapsed
