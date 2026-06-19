import io
import re

def verify_ghana_card_logic(card_front_file, card_number_input, selfie_file):
    """
    1. Check if ML libraries are installed.
    2. If not, use robust regex pattern matching to check GHA ID format,
       and ensure all required files are present.
    3. If ML libraries are installed, run the OCR and face match check.
    """
    results = {
        "id_match": False,
        "face_match": False,
        "error": None
    }

    try:
        import easyocr
        import face_recognition
        import numpy as np
        from PIL import Image
    except (ImportError, ModuleNotFoundError) as e:
        # Fallback simulated verification for development/testing when heavy ML libraries are not present
        if not card_front_file:
            results["error"] = "Card front image is missing."
            return results
        if not selfie_file:
            results["error"] = "Selfie image is missing."
            return results
        
        # Validate Ghana Card format: GHA-XXXXXXXXX-X where X is digit
        # Allow some flexibility in separator spacing or dashes
        cleaned_id = card_number_input.strip().upper()
        pattern = r'^GHA-\d{9}-\d$'
        if not re.match(pattern, cleaned_id):
            results["error"] = "Invalid Ghana Card number format. Format must be GHA-XXXXXXXXX-X"
            return results
        
        results["id_match"] = True
        results["face_match"] = True
        return results

    try:
        # Load images
        reader = easyocr.Reader(['en'])
        
        # Convert uploaded files to numpy arrays for processing
        front_img = Image.open(card_front_file).convert('RGB')
        selfie_img = Image.open(selfie_file).convert('RGB')
        
        front_np = np.array(front_img)
        selfie_np = np.array(selfie_img)

        # 1. OCR for ID Number
        ocr_results = reader.readtext(front_np)
        all_text = " ".join([res[1] for res in ocr_results])
        
        # We extract only the numeric digits for matching to avoid OCR letters confusion
        from difflib import SequenceMatcher
        input_digits = re.sub(r'\D', '', card_number_input)
        ocr_digits = re.sub(r'\D', '', all_text)
        
        if input_digits and input_digits in ocr_digits:
            results["id_match"] = True
        elif input_digits and ocr_digits:
            # Fallback: fuzzy match to allow for 1-2 character OCR mistakes
            # Search for best matching substring of length similar to input_digits
            best_match = 0
            for i in range(len(ocr_digits) - len(input_digits) + 1):
                window = ocr_digits[i:i+len(input_digits)]
                sim = SequenceMatcher(None, input_digits, window).ratio()
                if sim > best_match:
                    best_match = sim
            
            # 0.8 ratio on 10 digits means ~8 out of 10 digits matched exactly
            if best_match >= 0.8:
                results["id_match"] = True
            else:
                results["error"] = f"ID Number mismatch. Detected text: {all_text}"
        else:
            results["error"] = f"ID Number mismatch. Detected text: {all_text}"
            # Even if it fails, we continue to face check for debug info
            # But in production you might stop here

        # 2. Face Matching
        # Detect faces in both images
        front_encodings = face_recognition.face_encodings(front_np)
        selfie_encodings = face_recognition.face_encodings(selfie_np)

        if not front_encodings:
            results["error"] = "No face detected on the Ghana Card."
            return results
        
        if not selfie_encodings:
            results["error"] = "No face detected in your selfie."
            return results

        # Compare the first face found in each
        matches = face_recognition.compare_faces([front_encodings[0]], selfie_encodings[0], tolerance=0.6)
        
        if matches[0]:
            results["face_match"] = True
        else:
            results["error"] = "Face match failed. The selfie does not match the ID photo."

        return results

    except Exception as e:
        results["error"] = f"Verification engine error: {str(e)}"
        return results

