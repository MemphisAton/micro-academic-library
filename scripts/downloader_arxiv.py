import requests
import xml.etree.ElementTree as ET

ARXIV_API_URL = "http://export.arxiv.org/api/query"

def fetch_arxiv_papers(limit: int = 100, category: str = "cs.AI"):
    """
    Загружает статьи с arXiv через API. Возвращает список словарей с полями:
    title, summary, pdf_link, year, source.
    """
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    response = requests.get(ARXIV_API_URL, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    papers = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        summary = entry.find("atom:summary", ns).text.strip()
        links = entry.findall("atom:link", ns)

        pdf_link = None
        for link in links:
            if link.attrib.get("title") == "pdf":
                pdf_link = link.attrib["href"]
                break

        if not pdf_link:
            continue

        published = entry.find("atom:published", ns).text
        year = int(published[:4])

        papers.append({
            "title": title,
            "summary": summary,
            "pdf_link": pdf_link,
            "year": year,
            "source": "arXiv"
        })

    return papers

