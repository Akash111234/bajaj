from fastapi import FastAPI, UploadFile, File
from PIL import Image
import re
import pytesseract
import json
from io import BytesIO

# Path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize FastAPI app
app = FastAPI()

def parse_lab_data(text):
    print("🔍 Parsing OCR text for lab tests...")
    
    lab_tests = []
    
    pattern = re.compile(
        r'(?P<test_name>[A-Za-z \-/()]+)[\s:]+(?P<value>[-+]?\d*\.?\d+)\s*(?P<unit>[a-zA-Z/%]*)[\s\-:]*\(?(?P<ref_range>\d+\.?\d*\s*[-–]\s*\d+\.?\d*)\)?',
        re.IGNORECASE
    )

    for match in pattern.finditer(text):
        try:
            test_name = match.group('test_name').strip()
            value = float(match.group('value'))
            unit = match.group('unit').strip()
            ref_range = match.group('ref_range').strip()

            low, high = map(lambda x: float(x.strip()), re.split(r'[-–]', ref_range))
            out_of_range = not (low <= value <= high)

            lab_tests.append({
                "test_name": test_name,
                "test_value": str(value),  # Convert to string if needed for UI consistency
                "test_unit": unit,
                "bio_reference_range": ref_range,
                "lab_test_out_of_range": out_of_range
            })
        except Exception as e:
            print("⚠️ Skipped malformed entry:", e)
            continue

    return lab_tests

def extract_from_image(image_bytes):
    print("📂 Loading image from uploaded file...")
    image = Image.open(BytesIO(image_bytes))
    print("🖼️ Image loaded")

    text = pytesseract.image_to_string(image)
    print("🔍 OCR completed")

    data = parse_lab_data(text)
    return data

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    print(f"📂 Received file: {file.filename}")
    
    # Read the image file content
    image_bytes = await file.read()
    
    # Extract data from image
    data = extract_from_image(image_bytes)
    
    # Prepare the response
    response = {
        "is_success": True,
        "data": data
    }

    return response

# Example usage
if __name__ == "__main__":
    # Uncomment the below line to run the app locally
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    pass
