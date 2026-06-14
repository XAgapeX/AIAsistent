import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Używamy najnowszego modelu flash
model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_code_with_gemini(code, language):
    """
    Analizuje kod pod kątem jakości, błędów i testowalności za pomocą Gemini AI jako Ekspert QA.
    """
    prompt = f"""
Jesteś Ekspertem QA i Inżynierem Jakości Oprogramowania. Twoim zadaniem jest wsparcie testera w analizie kodu.
Analizujesz kod pod kątem jakości, wykrywasz błędy logiczne, podatności oraz proponujesz scenariusze testowe.
Odpowiadasz precyzyjnie, zwięźle i profesjonalnie.

TWOJE ZADANIA:
1. Oceń kod w skali 0-10 (gdzie 10 to kod produkcyjny najwyższej jakości, bezpieczny i przetestowany).
2. Zidentyfikuj konkretne błędy (bugs), wąskie gardła i problemy z bezpieczeństwem.
3. Zaproponuj konkretne scenariusze testowe (edge cases, happy path, boundary conditions).
4. Przygotuj poprawioną, zoptymalizowaną wersję kodu.

ZASADY PUNKTACJI:
- 0-3: Kod niebezpieczny, zawierający krytyczne błędy logiczne lub hardkodowane wrażliwe dane.
- 4-6: Kod działający, ale o słabej strukturze, braku walidacji lub podatny na błędy brzegowe.
- 7-8: Dobry kod, bezpieczny, wymagający jedynie drobnych poprawek w optymalizacji lub czytelności.
- 9-10: Kod doskonały, w pełni zabezpieczony, z obsługą błędów i gotowy do testów jednostkowych.

Zwróć wynik WYŁĄCZNIE w formacie JSON:
{{
    "quality_score": liczba (0-10),
    "issues": ["lista wykrytych błędów i ryzyk"],
    "suggestions": ["lista sugestii poprawy jakości"],
    "test_scenarios": ["lista konkretnych przypadków testowych do sprawdzenia"],
    "corrected_code": "POPRAWIONY KOD - BEZ KOMENTARZY"
}}

KOD DO ANALIZY ({language}):
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
    """Zapewnia, że quality_score mieści się w przedziale 0-10."""
    if isinstance(data, dict):
        if "quality_score" in data:
            score = data["quality_score"]
            if isinstance(score, (int, float)):
                data["quality_score"] = max(0, min(10, int(score)))
        if "corrected_code" not in data:
            data["corrected_code"] = ""
    return data


def remove_comments_from_code(data):
    """Usuwa komentarze Pythona i JavaScriptu z corrected_code."""
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
