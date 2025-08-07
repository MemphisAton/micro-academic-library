import json
import os
from io import BytesIO

from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, APIConnectionError

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from the first 5 pages of a PDF file."""
    reader = PdfReader(BytesIO(pdf_bytes))
    text = []

    for page in reader.pages[:5]:
        extracted = page.extract_text()
        if extracted:
            cleaned = clean_text(extracted)
            text.append(cleaned)

    return "\n".join(text)


def call_openai_chat(prompt: str, temperature: float = 0.4) -> str:
    """Low-level wrapper for OpenAI Chat API call. Returns raw response text."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except (APIConnectionError, AuthenticationError) as e:
        print(f"❌ OpenAI connection error: {e}")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
    return ""


def extract_metadata_from_pdf(pdf_bytes: bytes) -> dict:
    """Use OpenAI to extract structured metadata from a scientific PDF."""
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
        f"{text[:4000]}"
    )

    raw = call_openai_chat(prompt, temperature=0.4)

    if not raw:
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("⚠️ JSON parse error:", raw)
        return {}


def check_openai_available() -> bool:
    """Returns True if OpenAI API is available, otherwise False."""
    response = call_openai_chat("ping", temperature=0)
    return bool(response)


def clean_text(text: str) -> str:
    return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
