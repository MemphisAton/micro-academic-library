from openai import OpenAI
from io import BytesIO
from PyPDF2 import PdfReader
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    text = []
    for page in reader.pages[:5]:  # ограничим 5 страницами
        extracted = page.extract_text()
        if extracted:
            text.append(extracted)
    return "\n".join(text)


def extract_metadata_from_pdf(pdf_bytes: bytes) -> dict:
    text = extract_text_from_pdf(pdf_bytes)

    prompt = (
        "You are an AI assistant for an academic library.\n"
        "You are given the text of a scientific publication. Extract the following metadata and return it strictly as a valid JSON object with these fields:\n"
        "- title: Title of the paper\n"
        "- summary: Short summary (up to 5 sentences)\n"
        "- tags: List of 5–10 keywords\n"
        "- language: Language of the paper (e.g. en, ru, etc.)\n"
        "- organization: Institution or organization that published the paper (if found)\n"
        "- country: Country of the organization (if found)\n\n"
        "Here is the text:\n"
        f"{text[:8000]}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        raw = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw)
            return data
        except json.JSONDecodeError:
            print("⚠️ JSON parse error:", raw)
            return {}

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return {}
