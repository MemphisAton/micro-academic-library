import xml.etree.ElementTree as ET

import requests

ARXIV_API_URL = "http://export.arxiv.org/api/query"


def fetch_arxiv_papers(limit: int = 100, category: str = "cs.AI", start: int = 0):
    """Fetch recent arXiv papers by category and return parsed metadata."""

    params = {
        "search_query": f"cat:{category}",
        "start": start,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",

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


def fetch_arxiv_categories() -> dict:
    """
    Returns a dict of arXiv categories with their names.
    This is a hardcoded map as arXiv does not provide a public API for categories.
    """
    return {
        "math.PR": "Probability",
        "math.ST": "Statistics Theory",
        "cs.AI": "Artificial Intelligence",
        "cs.CL": "Computation and Language",
        "cs.LG": "Machine Learning",
        "cs.CV": "Computer Vision and Pattern Recognition",
        "cs.NI": "Networking and Internet Architecture",
        "cs.SE": "Software Engineering",
        "stat.ML": "Machine Learning (Statistics)",
        "econ.EM": "Econometrics",
        # ... add more if needed
    }
