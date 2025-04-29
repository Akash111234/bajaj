from PIL import Image
import re
import pytesseract
import json

# Path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

def extract_from_image(image_path):
    print(f"📂 Loading image from: {image_path}")
    image = Image.open(image_path)
    print("🖼️ Image loaded")

    text = pytesseract.image_to_string(image)
    print("🔍 OCR completed")

    data = parse_lab_data(text)
    output = {
        "is_success": True,
        "data": data
    }

    # Print the JSON formatted nicely
    print(json.dumps(output, indent=4))

# Example usage
if __name__ == "__main__":
    extract_from_image(r"c:\Users\akash\Downloads\abh.png")
