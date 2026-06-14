import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash")


def analyze_code_with_gemini(code, language):
    """
    Analizuje kod pod kątem jakości, błędów i testowalności za pomocą Gemini AI jako Ekspert QA.
    """
    prompt = f"""
Jesteś Ekspertem QA i Inżynierem Jakości Oprogramowania (Senior SDET). Twoim zadaniem jest rygorystyczna, ale sprawiedliwa analiza kodu.
Analizujesz kod pod kątem czystości (Clean Code), wydajności, bezpieczeństwa i testowalności.

TWOJE ZADANIA:
1. Oceń kod w skali 0-10. Bądź obiektywny.
2. Zidentyfikuj konkretne błędy (bugs), luki bezpieczeństwa (np. hardcoded credentials) i antywzorce.
3. Zaproponuj scenariusze testowe (happy path, edge cases, security tests).
4. Przygotuj poprawioną wersję kodu, która implementuje Twoje sugestie.

ZASADY PUNKTACJI:
- 0-2: Kod krytycznie wadliwy, niebezpieczny lub kompletnie nieczytelny.
- 3-4: Kod działający, ale posiadający poważne luki bezpieczeństwa (np. hasła w kodzie) lub bardzo słabą strukturę.
- 5-6: Kod poprawny, ale wymagający znacznej refaktoryzacji, dodania walidacji i obsługi błędów.
- 7-8: Dobry kod, spełniający standardy, wymagający jedynie drobnych optymalizacji.
- 9-10: Kod klasy produkcyjnej, bezpieczny, zoptymalizowany i łatwo testowalny.

UWAGA: Jeśli kod to prosty przykład edukacyjny, nie obniżaj oceny drastycznie za brak złożonych struktur, ale zawsze punktuj brak bezpieczeństwa.

Zwróć wynik WYŁĄCZNIE w formacie JSON:
{{
    "quality_score": liczba (0-10),
    "issues": ["lista konkretnych problemów"],
    "suggestions": ["lista konkretnych ulepszeń"],
    "test_scenarios": ["scenariusze testowe"],
    "corrected_code": "POPRAWIONY KOD"
}}

KOD DO ANALIZY ({language}):
{code}
"""

    max_retries = 5
    for attempt in range(max_retries):
        try:

            response = model.generate_content(
                prompt,
                request_options={"timeout": 600}
            )

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
                # Zwiększamy opóźnienie z każdą próbą
                retry_delay = (attempt + 1) * 20
                print(f"Limit API przekroczony. Próba {attempt + 1}/{max_retries}. Ponowna próba za {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                return {
                    "quality_score": 0,
                    "issues": ["Przekroczono limit zapytań API (Quota Exceeded). Darmowe klucze mają limity (np. 2-15 zapytań na minutę). Poczekaj minutę i spróbuj ponownie."],
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


import re

def remove_comments_from_code(data):
    """
    Usuwa komentarze (jednoliniowe i wieloliniowe) z corrected_code dla różnych języków.
    """
    if isinstance(data, dict) and "corrected_code" in data:
        code = data["corrected_code"]
        
        # 1. Usuwanie komentarzy wieloliniowych: /* ... */ (JS, TS, Java, C#)
        # Oraz komentarzy typu docstring/multiline string: """ ... """ i ''' ... ''' (Python)
        # Używamy flagi re.DOTALL, aby kropka łapała też znaki nowej linii
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # 2. Usuwanie komentarzy jednoliniowych: // (JS, TS, Java, C#) oraz # (Python)
        # Musimy uważać, aby nie usunąć znaków wewnątrz stringów
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Prosta heurystyka dla komentarzy jednoliniowych
            # Szukamy // lub # i usuwamy wszystko po nich, chyba że są w cudzysłowie
            
            # Usuwamy puste komentarze typu // lub # na początku linii
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                continue
                
            # Szukamy komentarza na końcu linii
            new_line = ""
            in_string = False
            string_char = None
            i = 0
            while i < len(line):
                char = line[i]
                
                # Obsługa stringów
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                
                # Sprawdzanie komentarza (tylko poza stringiem)
                if not in_string:
                    if line[i:i+2] == '//':
                        break # Koniec linii (JS/TS/Java/C# comment)
                    if char == '#':
                        break # Koniec linii (Python comment)
                
                new_line += char
                i += 1
            
            if new_line.strip() or not line.strip():
                cleaned_lines.append(new_line.rstrip())
        
        data["corrected_code"] = '\n'.join(cleaned_lines).strip()

    return data
