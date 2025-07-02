from fastapi import FastAPI, File, UploadFile, HTTPException
from app.models import OCRResult
from app.ocr import process_file

app = FastAPI()

@app.post("/ocr", response_model=OCRResult)
async def ocr_endpoint(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="file_missing")

    content = await file.read()
    doc_type, full_text, fields, elapsed = process_file(content)
    
    print('#'*60)
    print('Doc Type')
    print('#'*60)
    print(doc_type)
    
    print('#'*60)
    print('Full Text')
    print('#'*60)
    print(full_text)
    
    print('#'*60)
    print('Fields')
    print('#'*60)
    print(fields)
    
    if not doc_type:
        raise HTTPException(status_code=422, detail="unsupported_document_type")

    return OCRResult(
        document_type=doc_type, 
        finalJson=fields, 
        total_time=elapsed
        )
