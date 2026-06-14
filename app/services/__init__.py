import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_code_with_gemini(code, language):
    prompt = f"""
You are a CODE QUALITY EXPERT. Rate code fairly based on SECURITY and STRUCTURE.

CRITICAL SCORING RULE - FOLLOW EXACTLY:

IF CODE USES bcrypt, scrypt, or argon2 for password hashing = MINIMUM 8/10!
If also has proper structure = 9-10/10!

SCORING BREAKDOWN:
1-2/10: Hardcoded plaintext passwords + SQL injection risks + no validation
3-4/10: Some hardcoded secrets but partial improvements
5-7/10: Some security measures but incomplete
8/10: Uses secure hashing (bcrypt/scrypt/argon2) + no SQL injection + basic structure
9-10/10: Excellent security (bcrypt/scrypt/argon2) + clean code + error handling

BCRYPT MEANS: This code is SECURE against:
✓ Brute force attacks (bcrypt is slow by design)
✓ Plaintext password exposure (hashed, not stored)
✓ Rainbow table attacks (bcrypt uses salt)
✓ Timing attacks (bcrypt.checkpw is constant-time)

If you see bcrypt.hashpw() and bcrypt.checkpw() = Code is SECURE = 8-10/10

Demo/test code with hardcoded passwords for testing is ACCEPTABLE with bcrypt = Score stays HIGH.
Only production code that stores plaintext passwords = Low score.

YOUR TASK:
1. Check if code uses secure hashing
2. Check for SQL injection vulnerabilities
3. Check code structure
4. Rate based on ACTUAL SECURITY, not theoretical improvements
5. IF USING BCRYPT = MINIMUM 8/10 (unless it has other critical flaws)

Return ONLY valid JSON:
{{
    "quality_score": number (apply rules: bcrypt=8+ minimum),
    "issues": ["issue 1" or "Code is secure"],
    "suggestions": ["suggestion 1" or "Code follows security best practices"],
    "corrected_code": "CLEAN CODE - ZERO COMMENTS"
}}

CODE:
{code}
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip()
            cleaned_response = cleaned_response.replace("```json", "")
            cleaned_response = cleaned_response.replace("```", "")
            cleaned_response = cleaned_response.strip()

            json_start = cleaned_response.find("{")
            json_end = cleaned_response.rfind("}") + 1
            cleaned_response = cleaned_response[json_start:json_end]

            result = json.loads(cleaned_response)
            result = normalize_quality_score(result)
            result = remove_comments_from_code(result)
            return result

        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                retry_delay = 16
                print(f"Quota exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return {
                    "quality_score": 0,
                    "issues": ["API quota exceeded. Please try again in a moment."],
                    "suggestions": []
                }

        except Exception as e:
            return {
                "quality_score": 0,
                "issues": [f"Error: {str(e)}"],
                "suggestions": []
            }


def normalize_quality_score(data):
    if isinstance(data, dict):
        if "quality_score" in data:
            score = data["quality_score"]
            if isinstance(score, (int, float)):
                data["quality_score"] = max(0, min(10, int(score)))
        if "corrected_code" not in data:
            data["corrected_code"] = ""
    return data


def remove_comments_from_code(data):
    if isinstance(data, dict) and "corrected_code" in data:
        code = data["corrected_code"]
        lines = code.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('#') and not stripped.startswith('//'):
                comment_idx = line.find('#')
                if comment_idx != -1:
                    in_string = False
                    quote_char = None
                    for i, char in enumerate(line[:comment_idx]):
                        if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                            if not in_string:
                                in_string = True
                                quote_char = char
                            elif char == quote_char:
                                in_string = False

                    if not in_string:
                        line = line[:comment_idx].rstrip()

                if line or not stripped:
                    cleaned_lines.append(line)

        data["corrected_code"] = '\n'.join(cleaned_lines).strip()

    return data

