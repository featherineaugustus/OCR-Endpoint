from pydantic import BaseModel
from typing import Optional

class OCRResult(BaseModel):
    document_type: str
    finalJson: dict
    total_time: Optional[float]
