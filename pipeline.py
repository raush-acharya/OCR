import pytesseract
import nltk
import json
import cv2
from PIL import Image
import numpy as np
import re
from rapidfuzz import fuzz
from datetime import datetime

nltk.data.path.append("./nltk_data")a

# Windows only: uncomment and set path to your Tesseract binary
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_clean_date(lines):
    """
    Extracts and cleans the date from OCR lines.
    Tries to convert to YYYY-MM-DD. Falls back to '2025-07-01'.
    """
    for line in lines:
        if "bill date" in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                date_raw = parts[1].strip()
            else:
                date_raw = line.lower().replace("bill date", "").strip()

            # clean known noise
            date_raw = date_raw.replace("=.", "").replace("Q", "0").strip()

            # find pattern like 24/Jul/2025
            match = re.search(r'(\d{1,2})/([A-Za-z]{3,9})/(\d{2,4})', date_raw)
            if match:
                day = match.group(1).zfill(2)
                month = match.group(2)[:3].capitalize()
                year = match.group(3)
                if len(year) == 2:
                    year = "20" + year

                try:
                    dt = datetime.strptime(f"{day}/{month}/{year}", "%d/%b/%Y")
                    return dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

            # fallback if parsing fails
            return "2025-07-01"
    return "2025-07-01"


def process_bill_image_and_categorize(
    img_path, dataset_path="dataset.json", output_path="items.json", threshold=70
):
    """
    Processes a bill image: OCR + NLP categorization.
    Returns list of extracted items.
    """
    # Step 1: OCR & extract items
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Image file not found at: {img_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    pil_img = Image.fromarray(thresh_img)

    text = pytesseract.image_to_string(pil_img)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    date_found = extract_clean_date(lines)

    remarks = "Unknown"
    for line in lines:
        if "customer" in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                remarks = parts[1].strip()
                break

    results = []
    item_pattern = re.compile(
        r'([A-Z\s.]+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)'
    )

    for line in lines:
        match = item_pattern.search(line)
        if match:
            results.append({
                "date": date_found,
                "item": match.group(1).strip(),
                "quantity": float(match.group(2)),
                "net_rate": float(match.group(3)),
                "net_amount": float(match.group(4)),
                "remarks": remarks
            })

    # Step 2: Categorize items
    with open(dataset_path, "r") as f:
        categories = json.load(f)

    category_keywords = []
    for category, keywords in categories.items():
        for keyword in keywords:
            category_keywords.append((keyword.lower(), category))

    for item in results:
        item_name = item.get("item", "").lower()
        assigned_category = "Uncategorized"
        highest_score = 0

        for keyword, category in category_keywords:
            score = fuzz.partial_ratio(keyword, item_name)
            if score > highest_score and score >= threshold:
                highest_score = score
                assigned_category = category

        item["category"] = assigned_category

    # Save updated items.json
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return results
